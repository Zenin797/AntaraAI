import { Outlet } from "react-router";
import "./Main.css";

export function App() {
  return (
    <div className="min-h-screen bg-bg text-text">
      <Outlet />
    </div>
  );
}
