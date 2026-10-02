import { useEffect, useState } from "react";
import { MyLocationRounded } from "@mui/icons-material";
import { Alert, Box, Chip, Paper, Stack } from "@mui/material";
import { getDevices, getEvents, getGeofences } from "../api";
import { MapView } from "../components/MapView";
import { PageHero } from "../components/PageHero";
import { Device, EventRecord, Geofence } from "../types";
import { useSearchParams } from "react-router-dom";
export function LiveMapPage() { const [fences, setFences] = useState<Geofence[]>([]), [events, setEvents] = useState<EventRecord[]>([]), [devices, setDevices] = useState<Device[]>([]), [searchParams] = useSearchParams(); const focusDeviceId = Number(searchParams.get("deviceId")) || undefined; useEffect(() => { const load = () => Promise.all([getGeofences(), getEvents(), getDevices()]).then(([f, e, d]) => { setFences(f); setEvents(e); setDevices(d); }); load(); const timer = window.setInterval(load, 15000); return () => window.clearInterval(timer); }, []); return <Box><PageHero title="Live map" subtitle="Live geofence boundaries and tracked-device positions." icon={<MyLocationRounded />} gradient="linear-gradient(135deg, #0f766e, #0ea5e9)" action={<Chip label={`${devices.filter(d => d.enabled).length} ACTIVE DEVICES`} sx={{ bgcolor: "rgba(255,255,255,.18)", color: "white", fontWeight: 800 }} />} /><Alert severity="info" sx={{ mb: 2, borderRadius: 2 }}>Map data refreshes every 15 seconds. Green markers indicate devices inside their latest evaluated geofence.</Alert><Paper sx={{ overflow: "hidden", border: "4px solid white" }}><MapView geofences={fences} events={events} devices={devices} focusDeviceId={focusDeviceId} /></Paper></Box>; }
