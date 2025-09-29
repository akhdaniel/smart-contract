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

  _parseFieldsString(fieldsString) {
    const fields = [];
    let currentField = '';
    let bracketCount = 0;

    for (let i = 0; i < fieldsString.length; i++) {
      const char = fieldsString[i];

      if (char === '[') {
        bracketCount++;
        currentField += char;
      } else if (char === ']') {
        bracketCount--;
        currentField += char;
      } else if (char === ',' && bracketCount === 0) {
        fields.push(currentField.trim());
        currentField = '';
      } else {
        currentField += char;
      }
    }
    fields.push(currentField.trim());

    return fields.filter(f => f !== '');
  },

  _buildSpecification(fieldsString) {
    const specification = {};
    const parsedFields = this._parseFieldsString(fieldsString);

    for (const fieldDef of parsedFields) {
      const one2manyMatch = fieldDef.match(/^(.*_ids)\[(.*)\]$/);
      if (one2manyMatch) {
        const relationName = one2manyMatch[1];
        const nestedFieldsString = one2manyMatch[2];
        specification[relationName] = {fields: this._buildSpecification(nestedFieldsString)};
      } else if (fieldDef.endsWith('_id')) {
        specification[fieldDef] = {fields:{display_name:{}}};
      } else {
        specification[fieldDef] = {};
      }
    }
    return specification;
  },

  async searchRead(model, domain = [], specification = {}, limit = 80) {
    // const specification = this._buildSpecification(fieldsString);
    const params = {
      model:model,
      method:'web_search_read',
      args:[],
      kwargs:{
        context:{uid: this.getUid()},
        domain:domain,
        specification: specification,
        limit: limit
      }
    }
    return await jsonrpc(`/web/dataset/call_kw/${model}/web_search_read`, params);

  },

  async read(model, ids, specification = {}) {
    // const specification = this._buildSpecification(fieldsString);
    const params = {
      model:model,
      method:'web_read',
      args:ids,
      kwargs:{
        context:{uid: this.getUid()},
        specification: specification
      }
    }
    return await jsonrpc(`/web/dataset/call_kw/${model}/web_read`, params);
  },

  async write(model, id, data={},specification={}) {
    const params = {
        model:model,
        method: 'web_save',
        args: [id, data], // data={documnet:'base6434827842878'}
        kwargs:{
          specification:specification,
          context:{uid: this.getUid()},
        }
    }
    return await jsonrpc(`/web/dataset/call_kw/${model}/web_write`, params);
  },

  getUid() {
    return parseInt(localStorage.getItem('uid'));
  }
};

export default odooService;
