import AppRoutes from "./routes"
import ErrorBoundary from "./components/shared/ErrorBoundary"
import ToastHost from "./components/ui/Toast"

function App(){
  return (
    <ErrorBoundary>
      <AppRoutes />
      <ToastHost />
    </ErrorBoundary>
  )
}

export default App;
