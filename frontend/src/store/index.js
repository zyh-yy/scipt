import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    scripts: [],
    chains: [],
    histories: [],
    loading: false,
    error: null
  },
  mutations: {
    setScripts(state, scripts) {
      state.scripts = scripts;
    },
    setChains(state, chains) {
      state.chains = chains;
    },
    setHistories(state, histories) {
      state.histories = histories;
    },
    setLoading(state, loading) {
      state.loading = loading;
    },
    setError(state, error) {
      state.error = error;
    }
  },
  actions: {
    // 脚本相关操作
    async fetchScripts({ commit }) {
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.get('/api/scripts');
        if (response.data.code === 0) {
          commit('setScripts', response.data.data || []);
        } else {
          commit('setError', response.data.message);
        }
      } catch (error) {
        commit('setError', error.message);
      } finally {
        commit('setLoading', false);
      }
    },
    
    // 脚本链相关操作
    async fetchChains({ commit }) {
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.get('/api/chains');
        if (response.data.code === 0) {
          commit('setChains', response.data.data || []);
        } else {
          commit('setError', response.data.message);
        }
      } catch (error) {
        commit('setError', error.message);
      } finally {
        commit('setLoading', false);
      }
    },
    
    // 执行历史相关操作
    async fetchHistories({ commit }) {
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.get('/api/execution/history');
        if (response.data.code === 0) {
          commit('setHistories', response.data.data || []);
        } else {
          commit('setError', response.data.message);
        }
      } catch (error) {
        commit('setError', error.message);
      } finally {
        commit('setLoading', false);
      }
    },
    
    // 执行脚本
    async executeScript({ commit }, { scriptId, params }) {
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.post(`/api/execution/script/${scriptId}`, params);
        return response.data;
      } catch (error) {
        commit('setError', error.message);
        throw error;
      } finally {
        commit('setLoading', false);
      }
    },
    
    // 执行脚本链
    async executeChain({ commit }, { chainId, params }) {
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.post(`/api/execution/chain/${chainId}`, params);
        return response.data;
      } catch (error) {
        commit('setError', error.message);
        throw error;
      } finally {
        commit('setLoading', false);
      }
    },
    
    // 获取脚本版本历史
    async fetchScriptVersions({ commit }, scriptId) {
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.get(`/api/scripts/${scriptId}/versions`);
        return response.data;
      } catch (error) {
        commit('setError', error.message);
        throw error;
      } finally {
        commit('setLoading', false);
      }
    },
    
    // 获取版本内容
    async fetchVersionContent({ commit }, { scriptId, versionId }) {
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.get(`/api/scripts/${scriptId}/versions/${versionId}/content`);
        return response.data;
      } catch (error) {
        commit('setError', error.message);
        throw error;
      } finally {
        commit('setLoading', false);
      }
    },
    
    // 比较版本差异
    async compareVersions({ commit }, { scriptId, versionId1, versionId2 }) {
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.get(`/api/scripts/${scriptId}/versions/compare/html`, {
          params: { version_id1: versionId1, version_id2: versionId2 }
        });
        return response.data;
      } catch (error) {
        commit('setError', error.message);
        throw error;
      } finally {
        commit('setLoading', false);
      }
    },
    
    // 回滚到指定版本
    async rollbackVersion({ commit }, { scriptId, versionId }) {
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.put(`/api/scripts/${scriptId}/versions/${versionId}/rollback`);
        return response.data;
      } catch (error) {
        commit('setError', error.message);
        throw error;
      } finally {
        commit('setLoading', false);
      }
    }
  },
  getters: {
    scriptById: state => id => {
      return state.scripts.find(script => script.id === id) || null;
    },
    chainById: state => id => {
      return state.chains.find(chain => chain.id === id) || null;
    },
    historyById: state => id => {
      return state.histories.find(history => history.id === id) || null;
    }
  }
});
