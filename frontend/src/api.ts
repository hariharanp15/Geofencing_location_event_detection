import axios from "axios";
import { AuditLog, Device, EventRecord, Geofence } from "./types";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api" });
export const getGeofences = () => api.get<Geofence[]>("/geofences").then(r => r.data);
export const getGeofence = (id: number) => api.get<Geofence>(`/geofences/${id}`).then(r => r.data);
export const saveGeofence = (fence: Omit<Geofence, "id">, id?: number) => id ? api.put<Geofence>(`/geofences/${id}`, fence).then(r => r.data) : api.post<Geofence>("/geofences", fence).then(r => r.data);
export const setGeofenceStatus = (id: number, enabled: boolean) => api.patch<Geofence>(`/geofences/${id}/status?enabled=${enabled}`).then(r => r.data);
export const deleteGeofence = (id: number) => api.delete(`/geofences/${id}`);
export const getDevices = () => api.get<Device[]>("/devices").then(r => r.data);
export const saveDevice = (device: Omit<Device, "id">, id?: number) => id ? api.put<Device>(`/devices/${id}`, device).then(r => r.data) : api.post<Device>("/devices", device).then(r => r.data);
export const setDeviceStatus = (id: number, enabled: boolean) => api.patch<Device>(`/devices/${id}/status?enabled=${enabled}`).then(r => r.data);
export const deleteDevice = (id: number) => api.delete(`/devices/${id}`);
export const getEvents = () => api.get<EventRecord[]>("/events").then(r => r.data);
export const getAuditLogs = () => api.get<AuditLog[]>("/audit-logs?limit=500").then(r => r.data);
