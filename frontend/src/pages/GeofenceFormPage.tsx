import { FormEvent, useEffect, useState } from "react";
import { Button, Checkbox, FormControlLabel, MenuItem, Stack, TextField, Typography } from "@mui/material";
import { useNavigate, useParams } from "react-router-dom";
import { getGeofence, saveGeofence } from "../api";
import { Geofence } from "../types";

type Draft = Omit<Geofence, "id">;
const empty: Draft = { name: "", boundary_type: "circle", enabled: true, center_latitude: 12.9716, center_longitude: 77.5946, radius_meters: 100, accuracy_buffer_meters: 15, tracking_interval_seconds: 60, event_rules: { enter: true, exit: true, inside: true, outside: true }, points: [] };

export function GeofenceFormPage() {
  const navigate = useNavigate(), { id } = useParams(), editing = Boolean(id);
  const [draft, setDraft] = useState<Draft>(empty);
  useEffect(() => { if (id) getGeofence(Number(id)).then(({ id: _, ...fence }) => setDraft(fence)); }, [id]);
  const set = <K extends keyof Draft>(key: K, value: Draft[K]) => setDraft(current => ({ ...current, [key]: value }));
  function submit(event: FormEvent) { event.preventDefault(); if (draft.boundary_type === "polygon" && draft.points.length < 3) return; saveGeofence(draft, id ? Number(id) : undefined).then(() => navigate("/geofences")); }
  const pointsText = draft.points.map(p => `${p.latitude},${p.longitude}`).join("; ");
  return <form onSubmit={submit}><Typography variant="h4" gutterBottom>{editing ? "Edit geofence" : "Create geofence"}</Typography><Stack spacing={2} maxWidth={600}>
    <TextField label="Name" required value={draft.name} onChange={e => set("name", e.target.value)} />
    <TextField select label="Boundary type" value={draft.boundary_type} onChange={e => set("boundary_type", e.target.value as Draft["boundary_type"])}><MenuItem value="circle">Circle</MenuItem><MenuItem value="polygon">Polygon</MenuItem></TextField>
    {draft.boundary_type === "circle" ? <><TextField label="Center latitude" type="number" required value={draft.center_latitude} onChange={e => set("center_latitude", Number(e.target.value))} inputProps={{ step: "any" }} /><TextField label="Center longitude" type="number" required value={draft.center_longitude} onChange={e => set("center_longitude", Number(e.target.value))} inputProps={{ step: "any" }} /><TextField label="Radius (meters)" type="number" required value={draft.radius_meters} onChange={e => set("radius_meters", Number(e.target.value))} /></> : <TextField label="Points (lat,lng; lat,lng; lat,lng)" required value={pointsText} onChange={e => set("points", e.target.value.split(";").filter(Boolean).map(point => { const [latitude, longitude] = point.trim().split(",").map(Number); return { latitude, longitude }; }))} helperText="Enter at least three points, separated by semicolons." />}
    <TextField label="GPS accuracy buffer (meters)" type="number" value={draft.accuracy_buffer_meters} onChange={e => set("accuracy_buffer_meters", Number(e.target.value))} />
    <TextField label="Tracking update interval (seconds)" type="number" required value={draft.tracking_interval_seconds} inputProps={{ min: 1, max: 86400 }} onChange={e => set("tracking_interval_seconds", Number(e.target.value))} helperText="Unchanged INSIDE or OUTSIDE statuses are recorded at this interval. ENTER and EXIT are always recorded immediately." />
    <Typography>Event rules</Typography>{Object.entries(draft.event_rules).map(([rule, checked]) => <FormControlLabel key={rule} label={rule} control={<Checkbox checked={checked} onChange={e => set("event_rules", { ...draft.event_rules, [rule]: e.target.checked })} />} />)}
    <Button type="submit" variant="contained">{editing ? "Save changes" : "Create geofence"}</Button>
  </Stack></form>;
}
