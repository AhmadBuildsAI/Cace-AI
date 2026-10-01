import api from './api';
import {
  GraphResponse, QueryResponse, QueryListItem,
  SecurityDashboard, DashboardData,
} from '../types';

export const getGraph = async (): Promise<GraphResponse> => {
  const r = await api.get('/graph/');
  return r.data;
};

export const submitQuery = async (query: string): Promise<QueryResponse> => {
  const r = await api.post('/query/', { query });
  return r.data;
};

export const listQueries = async (): Promise<QueryListItem[]> => {
  const r = await api.get('/query/');
  return r.data;
};

export const getQuery = async (id: string): Promise<QueryResponse> => {
  const r = await api.get(`/query/${id}`);
  return r.data;
};

export const getSecurityDashboard = async (): Promise<SecurityDashboard> => {
  const r = await api.get('/security/dashboard');
  return r.data;
};

export const getDashboard = async (): Promise<DashboardData> => {
  const r = await api.get('/analytics/dashboard');
  return r.data;
};

export const getModelInfo = async () => {
  const r = await api.get('/analytics/model-info');
  return r.data;
};
