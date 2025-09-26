import api from './api';

const ODOO_DB = import.meta.env.VITE_ODOO_DB

const jsonrpc = async (endpoint, params) => {
  try {
    const response = await api.post(endpoint, {
      jsonrpc: '2.0',
      method: 'call',
      params: params,
      id: Math.floor(Math.random() * 1000000000)
    }, {
      withCredentials: true
    });
    if (response.data.error) {
      // The interceptor will handle session expired errors.
      // If it's not a session expired error, we log it and return null.
      if (!(response.data.error.message === 'Odoo Session Expired' || (response.data.error.data && response.data.error.data.message === 'Session expired'))) {
        console.error('Odoo RPC Error:', response.data.error);
      }
      return null; // Always return null on Odoo RPC error
    }
    return response.data.result;
  } catch (error) {
    // The axios interceptor in main.js handles session expiration.
    // If the interceptor has already handled it (by rejecting the promise),
    // we don't need to log it again here.
    // For other network errors, we log and return null.
    if (!error.response || !error.response.data || !error.response.data.error || !(error.response.data.error.message === 'Odoo Session Expired' || (error.response.data.error.data && error.response.data.error.data.message === 'Session expired'))) {
        console.error('Network Error:', error);
    }
    return null; // Always return null on network error
  }
};

const odooService = {
  async login(username, password) {
    const result = await jsonrpc('/web/session/authenticate', {
      db: ODOO_DB,
      login: username,
      password: password,
    });
    if (result && result.uid) {
      // session_id is not directly exposed in get_session_info for security reasons
      // The session is managed by the browser via cookies.
      return result;
    }
    return null;
  },

  async getSessionInfo() {
    const sessionInfo = await jsonrpc('/web/session/get_session_info', {});
    return sessionInfo;
  },

  setSessionId(sid) {
    // With HttpOnly cookies, we don't need to set headers manually.
  },

  async searchRead(model, domain = [], fields = [], limit = 80) {
    const params = {
      model:model,
      method:'web_search_read',
      args:[],
      kwargs:{
        context:{uid: this.getUid()},
        domain:domain,
        specification:{
          name:{},
          start_date:{},
          izin_prinsip_id:{fields:{
            display_name:{}
          }},
        }
      }
    }
    return await jsonrpc(`/web/dataset/call_kw/${model}/web_search_read`, params);

  },

  async searchReadOld(model, domain = [], fields = [], limit = 80) {
    const params = {
        service: 'object',
        method: 'call',
        model:model,
        // args: [ODOO_DB, this.getUid(), false, model, 'search_read', [domain],],
        kwargs: {
          'context': {'uid': this.getUid()}, 
          'fields': fields, 'limit': limit
        }
    }
    return await jsonrpc('/jsonrpc', params);
  },
  async read(model, ids, domain = [], fields = [], limit = 80) {
    const params = {
      model:model,
      method:'web_read',
      args:ids,
      kwargs:{
        context:{uid: this.getUid()},
        // domain:domain,
        specification:{
          name:{},
          start_date:{},
          termin_ids:{
            fields:{
              name:{},
              nilai:{},
              persentase:{},
              stage_id:{fields:{display_name:{}}}
            }
          },
          payment_ids:{
            fields:{
              name:{}
            }
          },
          izin_prinsip_id:{fields:{
            display_name:{}
          }},
        }
      }
    }
    return await jsonrpc(`/web/dataset/call_kw/${model}/web_read`, params);

  },
  async readOld(model, ids, fields = []) {
    const params = {
        service: 'object',
        method: 'execute_kw',
        args: [ODOO_DB, this.getUid(), false, model, 'read', [ids], {'fields': fields, 'context': {'uid': this.getUid()}}]
    }
    return await jsonrpc('/jsonrpc', params);
  },

  async write(model, id, data) {
    const params = {
        service: 'object',
        method: 'execute_kw',
        args: [ODOO_DB, this.getUid(), false, model, 'write', [[id], data], {'context': {'uid': this.getUid()}}]
    }
    return await jsonrpc('/jsonrpc', params);
  },

  getUid() {
    return parseInt(localStorage.getItem('uid'));
  }
};

export default odooService;
