import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Button from "../../components/ui/Button";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import { getErrorMessage, parseApiError } from "../../services/api";

const emptyContext = {};

const asItems = (result) => {
  if (Array.isArray(result)) return result;
  return Array.isArray(result?.items) ? result.items : [];
};

const asTotal = (result) => {
  if (Number.isFinite(result?.total)) return result.total;
  if (Array.isArray(result)) return result.length;
  return 0;
};

const resolveConfig = (value, ...args) =>
  typeof value === "function" ? value(...args) : value;

const getInitialForm = (config, context) => ({
  ...(resolveConfig(config.initialForm, context) || {}),
});

const cleanPayload = (payload) =>
  Object.entries(payload).reduce((nextPayload, [key, value]) => {
    nextPayload[key] = value === "" ? null : value;
    return nextPayload;
  }, {});

function FormControl({ field, value, error, onChange }) {
  const commonProps = {
    name: field.name,
    value: value ?? "",
    onChange,
    required: field.required,
    disabled: field.disabled,
  };

  if (field.type === "select") {
    return (
      <div>
        <label className="mb-1.5 block text-sm font-medium text-text-soft">
          {field.label}
        </label>
        <select className="input-base" {...commonProps}>
          <option value="">{field.placeholder || "Select an option"}</option>
          {(field.options || []).map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {error && <p className="mt-1 text-sm text-error">{error}</p>}
      </div>
    );
  }

  if (field.type === "textarea") {
    return (
      <div>
        <label className="mb-1.5 block text-sm font-medium text-text-soft">
          {field.label}
        </label>
        <textarea
          className="input-base min-h-24"
          placeholder={field.placeholder}
          {...commonProps}
        />
        {error && <p className="mt-1 text-sm text-error">{error}</p>}
      </div>
    );
  }

  return (
    <Input
      label={field.label}
      type={field.type || "text"}
      placeholder={field.placeholder}
      min={field.min}
      max={field.max}
      step={field.step}
      error={error}
      {...commonProps}
    />
  );
}

function ResourcePage({ config }) {
  const [context, setContext] = useState(emptyContext);
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [formData, setFormData] = useState(() => getInitialForm(config, emptyContext));
  const [filters, setFilters] = useState(() => resolveConfig(config.initialFilters, emptyContext) || {});
  const [editingItem, setEditingItem] = useState(null);
  const [busyId, setBusyId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState(null);
  const contextRef = useRef(context);
  const filtersRef = useRef(filters);
  const editingItemRef = useRef(editingItem);

  useEffect(() => {
    contextRef.current = context;
  }, [context]);

  useEffect(() => {
    filtersRef.current = filters;
  }, [filters]);

  useEffect(() => {
    editingItemRef.current = editingItem;
  }, [editingItem]);

  const fields = useMemo(
    () => resolveConfig(config.fields, context, editingItem) || [],
    [config, context, editingItem]
  );
  const filterFields = useMemo(
    () => resolveConfig(config.filters, context) || [],
    [config, context]
  );
  const columns = useMemo(
    () => resolveConfig(config.columns, context) || [],
    [config, context]
  );

  const resetForm = useCallback(() => {
    setEditingItem(null);
    setFormData(getInitialForm(config, context));
    setFieldErrors({});
  }, [config, context]);

  const loadContext = useCallback(async () => {
    if (!config.loadContext) return emptyContext;
    const nextContext = await config.loadContext();
    const resolvedContext = nextContext || emptyContext;
    contextRef.current = resolvedContext;
    setContext(resolvedContext);
    setFormData((current) =>
      editingItemRef.current ? current : getInitialForm(config, resolvedContext)
    );
    return resolvedContext;
  }, [config]);

  const loadItems = useCallback(
    async (
      activeFilters = filtersRef.current,
      activeContext = contextRef.current
    ) => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await config.fetchItems(activeFilters, activeContext);
        setItems(asItems(result));
        setTotal(asTotal(result));
      } catch (err) {
        setError(getErrorMessage(err, `Failed to load ${config.pluralLabel}.`));
      } finally {
        setIsLoading(false);
      }
    },
    [config]
  );

  useEffect(() => {
    let isMounted = true;

    const loadPage = async () => {
      try {
        const nextContext = await loadContext();
        if (isMounted) {
          await loadItems(filters, nextContext);
        }
      } catch (err) {
        if (isMounted) {
          setError(getErrorMessage(err, "Failed to load page data."));
          setIsLoading(false);
        }
      }
    };

    loadPage();

    return () => {
      isMounted = false;
    };
  }, [filters, loadContext, loadItems]);

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
    setFieldErrors((current) => ({ ...current, [name]: undefined }));
    setError(null);
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccessMessage(null);
    setFieldErrors({});

    try {
      const payload = config.buildPayload
        ? config.buildPayload(formData, editingItem, context)
        : cleanPayload(formData);

      if (editingItem) {
        await config.updateItem(editingItem.id, payload);
        setSuccessMessage(`${config.singularLabel} updated successfully.`);
      } else {
        await config.createItem(payload);
        setSuccessMessage(`${config.singularLabel} created successfully.`);
      }

      resetForm();
      await loadItems();
    } catch (err) {
      const parsed = parseApiError(
        err,
        editingItem
          ? `Failed to update ${config.singularLabel.toLowerCase()}.`
          : `Failed to create ${config.singularLabel.toLowerCase()}.`
      );
      setFieldErrors(parsed.fieldErrors);
      setError(parsed.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setFormData(config.mapItemToForm(item, context));
    setSuccessMessage(null);
    setError(null);
    setFieldErrors({});
  };

  const handleDelete = async (item) => {
    const label = config.getItemLabel ? config.getItemLabel(item, context) : item.id;

    if (!window.confirm(`Delete ${label}? This cannot be undone.`)) {
      return;
    }

    setBusyId(item.id);
    setError(null);
    setSuccessMessage(null);

    try {
      await config.deleteItem(item.id);
      if (editingItem?.id === item.id) resetForm();
      setSuccessMessage(`${config.singularLabel} deleted successfully.`);
      await loadItems();
    } catch (err) {
      setError(getErrorMessage(err, `Failed to delete ${config.singularLabel.toLowerCase()}.`));
    } finally {
      setBusyId(null);
    }
  };

  const handleRefresh = async () => {
    const nextContext = await loadContext();
    await loadItems(filters, nextContext);
  };

  const clearFilters = () => {
    setFilters(resolveConfig(config.initialFilters, context) || {});
  };

  const showForm = config.canCreate || (config.canUpdate && editingItem);

  return (
    <div className="mx-auto max-w-7xl space-y-5">
      {error && (
        <div className="rounded-md border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-600">
          {error}
        </div>
      )}
      {successMessage && (
        <div className="rounded-md border border-green-500/40 bg-green-500/10 px-4 py-3 text-sm text-green-700">
          {successMessage}
        </div>
      )}

      <div className={`grid gap-5 ${showForm ? "xl:grid-cols-[420px_minmax(0,1fr)]" : ""}`}>
        {showForm && (
          <Card className="p-5">
            <h2 className="text-lg font-semibold">
              {editingItem ? `Edit ${config.singularLabel.toLowerCase()}` : `Create ${config.singularLabel.toLowerCase()}`}
            </h2>
            {config.formHelp && (
              <p className="mt-1 text-sm text-text-muted">{config.formHelp}</p>
            )}

            <form onSubmit={handleSubmit} className="mt-5 space-y-4">
              {fields
                .filter((field) => !field.hidden)
                .filter((field) => (editingItem ? field.showOnEdit !== false : field.showOnCreate !== false))
                .map((field) => (
                  <FormControl
                    key={field.name}
                    field={field}
                    value={formData[field.name]}
                    error={fieldErrors[field.name]}
                    onChange={handleFormChange}
                  />
                ))}

              <div className="flex flex-wrap gap-2">
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Saving..." : editingItem ? "Save changes" : "Create"}
                </Button>
                {editingItem && (
                  <Button type="button" variant="outline" onClick={resetForm}>
                    Cancel
                  </Button>
                )}
              </div>
            </form>
          </Card>
        )}

        <Card className="p-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <h2 className="text-lg font-semibold">{config.pluralLabel}</h2>
              <p className="mt-1 text-sm text-text-muted">
                {total} record{total === 1 ? "" : "s"} found.
              </p>
            </div>
            <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
              Refresh
            </Button>
          </div>

          {filterFields.length > 0 && (
            <form
              onSubmit={(event) => {
                event.preventDefault();
                loadItems(filters);
              }}
              className="mt-5 grid gap-3 rounded-md border border-border bg-background/70 p-4 md:grid-cols-3 xl:grid-cols-4"
            >
              {filterFields.map((field) => (
                <FormControl
                  key={field.name}
                  field={field}
                  value={filters[field.name]}
                  onChange={handleFilterChange}
                />
              ))}
              <div className="flex items-end gap-2">
                <Button type="submit" size="small">
                  Apply
                </Button>
                <Button type="button" variant="outline" size="small" onClick={clearFilters}>
                  Clear
                </Button>
              </div>
            </form>
          )}

          <div className="mt-5 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-border text-text-muted">
                <tr>
                  {columns.map((column) => (
                    <th key={column.key} className="py-3 pr-4 font-medium">
                      {column.label}
                    </th>
                  ))}
                  {(config.canUpdate || config.canDelete) && (
                    <th className="py-3 font-medium">Actions</th>
                  )}
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td
                      colSpan={columns.length + 1}
                      className="py-6 text-text-muted"
                    >
                      Loading {config.pluralLabel.toLowerCase()}...
                    </td>
                  </tr>
                ) : items.length === 0 ? (
                  <tr>
                    <td
                      colSpan={columns.length + 1}
                      className="py-6 text-text-muted"
                    >
                      No records found.
                    </td>
                  </tr>
                ) : (
                  items.map((item) => (
                    <tr key={item.id} className="border-b border-border/60">
                      {columns.map((column) => (
                        <td key={column.key} className="py-4 pr-4 align-top">
                          {column.render ? column.render(item, context) : item[column.key] || "N/A"}
                        </td>
                      ))}
                      {(config.canUpdate || config.canDelete) && (
                        <td className="py-4 align-top">
                          <div className="flex flex-wrap gap-2">
                            {config.canUpdate && (
                              <Button
                                type="button"
                                variant="outline"
                                size="small"
                                onClick={() => handleEdit(item)}
                                disabled={busyId === item.id}
                              >
                                Edit
                              </Button>
                            )}
                            {config.canDelete && (
                              <Button
                                type="button"
                                variant="danger"
                                size="small"
                                onClick={() => handleDelete(item)}
                                disabled={busyId === item.id}
                              >
                                {busyId === item.id ? "Deleting..." : "Delete"}
                              </Button>
                            )}
                          </div>
                        </td>
                      )}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default ResourcePage;
