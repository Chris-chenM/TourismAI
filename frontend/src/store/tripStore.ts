/* Zustand：仅存 UI 交互状态，不存表单/loading/error */

import { create } from "zustand";
import type { PlanResponse } from "../types/trip";

interface TripStore {
  trip: PlanResponse | null;
  setTrip: (trip: PlanResponse) => void;
  selectedDay: number;
  setSelectedDay: (day: number) => void;
  selectedPOI: [number, number] | null;
  setSelectedPOI: (pos: [number, number] | null) => void;
}

export const useTripStore = create<TripStore>((set) => ({
  trip: null,
  setTrip: (trip) => set({ trip, selectedDay: 1, selectedPOI: null }),
  selectedDay: 1,
  setSelectedDay: (day) => set({ selectedDay: day }),
  selectedPOI: null,
  setSelectedPOI: (pos) => set({ selectedPOI: pos }),
}));
