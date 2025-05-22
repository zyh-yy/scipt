#!/usr/bin/env node
/**
 * 数据库插入脚本 - JavaScript版本，XML输出
 * 使用Node.js和SQLite模块向数据库中插入数据，并以XML格式返回结果
 */

const fs = require('fs');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();

// 检查是否在Docker容器中运行
function isInDocker() {
    try {
        return fs.existsSync('/.dockerenv');
    } catch (err) {
        return false;
    }
}

// 查找数据库文件
function findDatabase() {
    const possiblePaths = [
        path.resolve(__dirname, '../database/scripts.db'),
        path.resolve(__dirname, './database/scripts.db'),
        path.resolve(__dirname, 'database/scripts.db'),
        '/app/database/scripts.db'
    ];

    for (const dbPath of possiblePaths) {
        try {
            if (fs.existsSync(dbPath)) {
                return dbPath;
            }
        } catch (err) {
            // 忽略错误，继续检查下一个路径
        }
    }
    return null;
}

// 生成XML输出
function generateXML(tagName, content, attributes = {}) {
    const attrs = Object.entries(attributes)
        .map(([key, value]) => `${key}="${escapeXML(value)}"`)
        .join(' ');
    
    if (typeof content === 'object' && content !== null) {
        const innerContent = Object.entries(content)
            .map(([key, value]) => {
                if (Array.isArray(value)) {
                    return value.map(item => generateXML(key, item)).join('');
                } else if (typeof value === 'object' && value !== null) {
                    return generateXML(key, value);
                } else {
                    return generateXML(key, value);
                }
            })
            .join('');
        return `<${tagName}${attrs ? ' ' + attrs : ''}>${innerContent}</${tagName}>`;
    } else {
        const contentStr = content !== null && content !== undefined ? escapeXML(content.toString()) : '';
        return `<${tagName}${attrs ? ' ' + attrs : ''}>${contentStr}</${tagName}>`;
    }
}

// 转义XML特殊字符
function escapeXML(str) {
    if (typeof str !== 'string') {
        return str;
    }
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');
}

// 生成随机ID
function generateRandomId(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// 主函数
async function main() {
    try {
        // 检查参数
        if (process.argv.length < 3) {
            const errorXml = generateXML('response', {
                status: 'error',
                message: '缺少参数文件',
                timestamp: new Date().toISOString(),
                environment: {
                    inDocker: isInDocker()
                }
            });
            console.log(`<?xml version="1.0" encoding="UTF-8"?>\n${errorXml}`);
            process.exit(1);
        }

        const paramsFile = process.argv[2];
        
        // 检查参数文件是否存在
        if (!fs.existsSync(paramsFile)) {
            const errorXml = generateXML('response', {
                status: 'error',
                message: `参数文件不存在: ${paramsFile}`,
                timestamp: new Date().toISOString(),
                environment: {
                    inDocker: isInDocker()
                }
            });
            console.log(`<?xml version="1.0" encoding="UTF-8"?>\n${errorXml}`);
            process.exit(1);
        }

        // 读取参数
        const params = JSON.parse(fs.readFileSync(paramsFile, 'utf8'));
        
        // 查找数据库
        const dbPath = findDatabase();
        if (!dbPath) {
            const errorXml = generateXML('response', {
                status: 'error',
                message: '无法找到数据库文件',
                timestamp: new Date().toISOString(),
                environment: {
                    inDocker: isInDocker()
                }
            });
            console.log(`<?xml version="1.0" encoding="UTF-8"?>\n${errorXml}`);
            process.exit(1);
        }

        // 连接数据库
        const db = new sqlite3.Database(dbPath);
        
        // 处理数据库操作
        const tableName = params.table_name || 'scripts';
        const recordCount = params.record_count || 2;
        const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
        
        // 创建一个Promise包装的数据库操作
        const insertRecords = () => {
            return new Promise((resolve, reject) => {
                const insertedRecords = [];
                
                // 开始事务
                db.serialize(() => {
                    db.run('BEGIN TRANSACTION');
                    
                    let completed = 0;
                    
                    // 插入指定数量的记录
                    for (let i = 0; i < recordCount; i++) {
                        const randomId = generateRandomId();
                        const scriptName = `JS脚本 ${randomId}`;
                        const filePath = `scripts/js_test_${randomId}.js`;
                        const description = `由db_insert_js_xml.js生成的测试数据 #${i+1}`;
                        const fileType = 'javascript';
                        
                        db.run(
                            `INSERT INTO ${tableName} (name, description, file_path, file_type, created_at, updated_at) 
                             VALUES (?, ?, ?, ?, ?, ?)`,
                            [scriptName, description, filePath, fileType, now, now],
                            function(err) {
                                if (err) {
                                    db.run('ROLLBACK');
                                    reject(err);
                                    return;
                                }
                                
                                const scriptId = this.lastID;
                                
                                // 保存插入的记录信息
                                const record = {
                                    id: scriptId,
                                    name: scriptName,
                                    description: description,
                                    file_path: filePath,
                                    file_type: fileType,
                                    created_at: now
                                };
                                
                                insertedRecords.push(record);
                                
                                // 如果参数中指定了添加参数
                                if (params.add_parameters) {
                                    const paramName = `js_param_${i+1}`;
                                    const paramDesc = `JavaScript脚本参数 #${i+1}`;
                                    const paramType = i % 2 === 0 ? 'string' : 'number';
                                    const isRequired = i % 2;
                                    const defaultValue = i % 2 === 0 ? `"default_${randomId}"` : `${i*10}`;
                                    
                                    db.run(
                                        `INSERT INTO script_parameters 
                                         (script_id, name, description, param_type, is_required, default_value)
                                         VALUES (?, ?, ?, ?, ?, ?)`,
                                        [scriptId, paramName, paramDesc, paramType, isRequired, defaultValue],
                                        function(err) {
                                            if (err) {
                                                db.run('ROLLBACK');
                                                reject(err);
                                                return;
                                            }
                                            
                                            const paramId = this.lastID;
                                            
                                            // 添加参数信息到记录中
                                            if (!record.parameters) {
                                                record.parameters = [];
                                            }
                                            
                                            record.parameters.push({
                                                id: paramId,
                                                name: paramName,
                                                description: paramDesc,
                                                param_type: paramType,
                                                is_required: isRequired,
                                                default_value: defaultValue
                                            });
                                            
                                            completed++;
                                            if (completed === recordCount) {
                                                db.run('COMMIT');
                                                resolve(insertedRecords);
                                            }
                                        }
                                    );
                                } else {
                                    completed++;
                                    if (completed === recordCount) {
                                        db.run('COMMIT');
                                        resolve(insertedRecords);
                                    }
                                }
                            }
                        );
                    }
                });
            });
        };
        
        // 执行数据库操作
        const insertedRecords = await insertRecords();
        
        // 关闭数据库连接
        db.close();
        
        // 生成XML响应
        const responseXml = generateXML('response', {
            status: 'success',
            message: `成功插入 ${insertedRecords.length} 条记录到 ${tableName} 表`,
            timestamp: new Date().toISOString(),
            environment: {
                inDocker: isInDocker(),
                databasePath: dbPath
            },
            data: {
                records: insertedRecords
            }
        });
        
        // 输出XML响应
        console.log(`<?xml version="1.0" encoding="UTF-8"?>\n${responseXml}`);
        process.exit(0);
        
    } catch (error) {
        // 处理错误
        const errorXml = generateXML('response', {
            status: 'error',
            message: `执行出错: ${error.message}`,
            timestamp: new Date().toISOString(),
            environment: {
                inDocker: isInDocker()
            },
            error: {
                name: error.name,
                stack: error.stack
            }
        });
        
        console.log(`<?xml version="1.0" encoding="UTF-8"?>\n${errorXml}`);
        process.exit(1);
    }
}

// 执行主函数
main();
