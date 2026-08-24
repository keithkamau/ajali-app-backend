import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { incidentApi } from './incidentApi';

const getError = (error) => error.message || 'Unable to load incidents.';

export const fetchIncidents = createAsyncThunk('incidents/fetchAll', (params) => incidentApi.list(params));
export const fetchIncident = createAsyncThunk('incidents/fetchOne', (id) => incidentApi.get(id));
export const createIncident = createAsyncThunk('incidents/create', (incident) => incidentApi.create(incident));
export const updateIncident = createAsyncThunk('incidents/update', ({ id, incident }) => incidentApi.update(id, incident));
export const deleteIncident = createAsyncThunk('incidents/delete', (id) => incidentApi.remove(id));

const initialState = {
  incidents: [],
  currentIncident: null,
  loading: false,
  error: null,
};

const incidentSlice = createSlice({
  name: 'incidents',
  initialState,
  reducers: {
    clearIncidentError: (state) => { state.error = null; },
    clearCurrentIncident: (state) => { state.currentIncident = null; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchIncidents.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchIncidents.fulfilled, (state, action) => {
        state.loading = false;
        state.incidents = action.payload.incidents || action.payload;
      })
      .addCase(fetchIncident.fulfilled, (state, action) => { state.currentIncident = action.payload.incident || action.payload; })
      .addCase(createIncident.fulfilled, (state, action) => {
        state.incidents.unshift(action.payload.incident || action.payload);
      })
      .addCase(updateIncident.fulfilled, (state, action) => {
        const updated = action.payload.incident || action.payload;
        state.currentIncident = updated;
        state.incidents = state.incidents.map((incident) => incident.id === updated.id ? updated : incident);
      })
      .addCase(deleteIncident.fulfilled, (state, action) => {
        state.incidents = state.incidents.filter((incident) => incident.id !== action.meta.arg);
      })
      .addMatcher((action) => action.type.startsWith('incidents/') && action.type.endsWith('/rejected'), (state, action) => {
        state.loading = false;
        state.error = getError(action.error);
      });
  },
});

export const { clearIncidentError, clearCurrentIncident } = incidentSlice.actions;
export default incidentSlice.reducer;
