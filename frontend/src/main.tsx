import React from "react";
import ReactDOM from "react-dom/client";
import { CssBaseline, ThemeProvider, alpha, createTheme } from "@mui/material";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
const theme = createTheme({
  palette: { primary: { main: "#246bfd" }, secondary: { main: "#14b8a6" }, background: { default: "#f3f7fc", paper: "#ffffff" } },
  shape: { borderRadius: 12 },
  typography: { fontFamily: "Inter, Segoe UI, Arial, sans-serif", h4: { fontWeight: 750, letterSpacing: "-0.03em" }, h6: { fontWeight: 700 } },
  components: {
    MuiPaper: { styleOverrides: { root: { boxShadow: "0 10px 30px rgba(28, 53, 87, 0.06)", border: "1px solid #e5edf7" } } },
    MuiTableContainer: { styleOverrides: { root: { borderRadius: 12, border: "1px solid #e5edf7" } } },
    MuiTableHead: { styleOverrides: { root: { background: "linear-gradient(90deg, #f1f6ff, #f8fbff)" } } },
    MuiTableCell: { styleOverrides: { head: { color: "#486581", fontWeight: 750, textTransform: "uppercase", fontSize: "0.72rem", letterSpacing: "0.06em", borderBottom: "1px solid #dbe7f4" }, root: { borderBottom: "1px solid #edf2f7", paddingTop: 14, paddingBottom: 14 } } },
    MuiTableRow: { styleOverrides: { root: { "&:hover": { backgroundColor: alpha("#246bfd", 0.035) } } } },
    MuiButton: { styleOverrides: { root: { borderRadius: 9, fontWeight: 700, textTransform: "none", boxShadow: "none" } } },
    MuiChip: { styleOverrides: { root: { fontWeight: 700 } } }
  }
});
ReactDOM.createRoot(document.getElementById("root")!).render(<React.StrictMode><ThemeProvider theme={theme}><CssBaseline /><BrowserRouter><App /></BrowserRouter></ThemeProvider></React.StrictMode>);
