import EmptyState from "./EmptyState";
import LoadingState from "./LoadingState";

function DataTable({
  columns = [],
  data = [],
  isLoading = false,
  emptyTitle = "No records found",
  emptyDescription = "Try adjusting your filters or create a new record.",
}) {
  if (isLoading) return <LoadingState label="Loading records..." />;

  if (data.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={item.id || index}>
              {columns.map((column) => (
                <td key={column.key} data-label={column.label}>
                  <span>{column.render ? column.render(item) : item[column.key] || "-"}</span>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
