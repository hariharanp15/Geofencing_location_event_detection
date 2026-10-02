import { ReactNode } from "react";
import { Box, Stack, Typography } from "@mui/material";

export function PageHero({ title, subtitle, icon, gradient, action }: { title: string; subtitle: string; icon: ReactNode; gradient: string; action?: ReactNode }) {
  return <Box sx={{ mb: 3, px: { xs: 2.5, md: 3.5 }, py: 3, borderRadius: 3, color: "white", position: "relative", overflow: "hidden", background: gradient, boxShadow: "0 16px 30px rgba(29, 78, 216, .18)" }}><Box sx={{ position: "absolute", right: -15, top: -26, opacity: .15, "& svg": { fontSize: 150 } }}>{icon}</Box><Stack direction={{ xs: "column", sm: "row" }} alignItems={{ sm: "center" }} justifyContent="space-between" gap={2} position="relative"><Box><Typography variant="h4" color="inherit">{title}</Typography><Typography sx={{ opacity: .86 }}>{subtitle}</Typography></Box>{action}</Stack></Box>;
}
