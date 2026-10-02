import { Circle, MapContainer, Polygon, Popup, TileLayer, useMap } from "react-leaflet";
import { useEffect } from "react";
import { Device, EventRecord, Geofence } from "../types";
import "leaflet/dist/leaflet.css";

function FocusDevice({ device }: { device?: Device }) { const map = useMap(); useEffect(() => { if (device?.latitude != null && device.longitude != null) map.flyTo([device.latitude, device.longitude], 16, { duration: 0.75 }); }, [device, map]); return null; }
export function MapView({ geofences, events, devices = [], focusDeviceId }: { geofences: Geofence[]; events: EventRecord[]; devices?: Device[]; focusDeviceId?: number }) {
  const currentByDevice = new Map<string, EventRecord>();
  [...events].sort((a, b) => +new Date(b.occurred_at) - +new Date(a.occurred_at)).forEach(event => { if (!currentByDevice.has(event.device_external_id)) currentByDevice.set(event.device_external_id, event); });
  const focusedDevice = devices.find(device => device.id === focusDeviceId);
  return <MapContainer center={[12.9716, 77.5946]} zoom={12} style={{ height: "calc(100vh - 100px)", minHeight: 500 }}><FocusDevice device={focusedDevice} />
    <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    {geofences.map(f => f.boundary_type === "circle" && f.center_latitude != null && f.center_longitude != null ?
      <Circle key={f.id} center={[f.center_latitude, f.center_longitude]} radius={f.radius_meters ?? 0} pathOptions={{ color: f.enabled ? "#1976d2" : "#999" }}><Popup>{f.name}</Popup></Circle> :
      <Polygon key={f.id} positions={f.points.map(p => [p.latitude, p.longitude])}><Popup>{f.name}</Popup></Polygon>)}
    {[...currentByDevice.values()].map(e => <Circle key={e.device_external_id} center={[e.latitude, e.longitude]} radius={12} pathOptions={{ color: e.current_state === "inside" ? "#2e7d32" : "#ed6c02", fillOpacity: 1 }}><Popup><b>{e.device_external_id}</b><br />Current state: {e.current_state}<br />{e.geofence_name}</Popup></Circle>)}
    {devices.filter(d => d.latitude != null && d.longitude != null && !currentByDevice.has(d.external_id)).map(d => <Circle key={d.id} center={[d.latitude!, d.longitude!]} radius={12} pathOptions={{ color: "#1976d2", fillOpacity: 1 }}><Popup><b>{d.label}</b><br />{d.external_id}<br />No evaluated geofence event yet</Popup></Circle>)}
  </MapContainer>;
}
