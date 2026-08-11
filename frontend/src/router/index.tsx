import { Routes, Route } from "react-router-dom";
import HomePage from "../pages/HomePage";
import TripPage from "../pages/TripPage";
import HistoryPage from "../pages/HistoryPage";

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/trip" element={<TripPage />} />
      <Route path="/history" element={<HistoryPage />} />
    </Routes>
  );
}
