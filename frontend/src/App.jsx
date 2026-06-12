import AppRoutes from "./routes"
import ErrorBoundary from "./components/shared/ErrorBoundary"

function App(){
  return (
    <ErrorBoundary>
      <AppRoutes />
    </ErrorBoundary>
  )
}

export default App;
