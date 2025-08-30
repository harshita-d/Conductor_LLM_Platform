import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HealthStatus from "./components/HealthStatus";
import ChatScreen from "./components/chat/ChatScreen";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HealthStatus />} />
        <Route path="/chat" element={<ChatScreen />} />
      </Routes>
    </Router>
  );
}

export default App;
