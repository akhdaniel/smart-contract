import axios from 'axios'

const ODOO_URL = import.meta.env.VITE_ODOO_URL
const ODOO_DB = import.meta.env.VITE_ODOO_DB

const jsonrpc = async (endpoint, params) => {
  try {
    const response = await axios.post(`${ODOO_URL}${endpoint}`, {
      jsonrpc: '2.0',
      method: 'call',
      params: params,
      id: Math.floor(Math.random() * 1000000000)
    }, {
      withCredentials: true // Important for passing cookies
    });
    if (response.data.error) {
      console.error('Odoo RPC Error:', response.data.error);
      return null;
    }
    return response.data.result;
  } catch (error) {
    console.error('Network Error:', error);
    return null;
  }
};

const odooService = {
  async login(username, password) {
    const params = {
      service: 'common',
      method: 'login',
      args: [ODOO_DB, username, password, {}]
    };
    const uid = await jsonrpc('/jsonrpc', params);
    if (uid) {
        const sessionInfo = await this.getSessionInfo();
        return { uid: uid, sid: sessionInfo.session_id, user_context: sessionInfo.user_context };
    }
    return null;
  },

  async getSessionInfo() {
    return await jsonrpc('/web/session/get_session_info', {});
  },

  setSessionId(sid) {
    // With HttpOnly cookies, we don't need to set headers manually.
  },

  async searchRead(model, domain = [], fields = [], limit = 80) {
    const params = {
        service: 'object',
        method: 'execute_kw',
        args: [ODOO_DB, this.getUid(), "dummy_password", model, 'search_read', [domain], {'fields': fields, 'limit': limit}]
    }
    return await jsonrpc('/jsonrpc', params);
  },

  async read(model, ids, fields = []) {
    const params = {
        service: 'object',
        method: 'execute_kw',
        args: [ODOO_DB, this.getUid(), "dummy_password", model, 'read', [ids], {'fields': fields}]
    }
    return await jsonrpc('/jsonrpc', params);
  },

  async write(model, id, data) {
    const params = {
        service: 'object',
        method: 'execute_kw',
        args: [ODOO_DB, this.getUid(), "dummy_password", model, 'write', [[id], data]]
    }
    return await jsonrpc('/jsonrpc', params);
  },

  getUid() {
    return parseInt(localStorage.getItem('uid'));
  }
};

export default odooService;
