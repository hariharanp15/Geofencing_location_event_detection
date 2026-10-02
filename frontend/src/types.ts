export type Point = { latitude: number; longitude: number };
export type Geofence = { id: number; name: string; boundary_type: "circle" | "polygon"; enabled: boolean; center_latitude?: number; center_longitude?: number; radius_meters?: number; accuracy_buffer_meters: number; tracking_interval_seconds: number; event_rules: Record<string, boolean>; points: Point[] };
export type Device = { id: number; external_id: string; label: string; user_id?: number | null; enabled: boolean; latitude?: number | null; longitude?: number | null };
export type EventRecord = { id: number; event_type: string; previous_state: string | null; current_state: string; occurred_at: string; latitude: number; longitude: number; geofence_id: number; geofence_name: string; device_name: string; device_external_id: string };
export type AuditLog = { id: number; action: string; entity_type: string; entity_id: string; details: string | null; created_at: string };
