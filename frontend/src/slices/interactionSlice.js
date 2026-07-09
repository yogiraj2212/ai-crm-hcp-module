import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { submitForm, sendChatMessage } from "../api";

export const submitInteractionForm = createAsyncThunk(
  "interaction/submitForm",
  async (payload) => submitForm(payload)
);

export const sendMessage = createAsyncThunk(
  "interaction/sendMessage",
  async ({ hcp_id, rep_id, message, history }) =>
    sendChatMessage({ hcp_id, rep_id, message, history })
);

const initialState = {
  mode: "form",          // "form" | "chat"
  chatHistory: [],        // [{role, content}]
  lastResult: null,       // last logged interaction (form path)
  status: "idle",         // idle | loading | succeeded | failed
  error: null,
};

const interactionSlice = createSlice({
  name: "interaction",
  initialState,
  reducers: {
    setMode(state, action) {
      state.mode = action.payload;
    },
    resetResult(state) {
      state.lastResult = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitInteractionForm.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(submitInteractionForm.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.lastResult = action.payload;
      })
      .addCase(submitInteractionForm.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      })
      .addCase(sendMessage.pending, (state) => {
        state.status = "loading";
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.chatHistory = action.payload.history;
        if (action.payload.ready_to_log && action.payload.draft_interaction) {
          state.lastResult = {
            ...action.payload.draft_interaction,
            id: action.payload.saved_interaction_id,
          };
        }
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      });
  },
});

export const { setMode, resetResult } = interactionSlice.actions;
export default interactionSlice.reducer;
