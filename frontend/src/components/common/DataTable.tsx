import React from 'react';
import clsx from 'clsx';

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (item: T) => void;
  selectedId?: string;
  keyExtractor: (item: T) => string;
  emptyMessage?: string;
}

export function DataTable<T>({ 
  columns, 
  data, 
  onRowClick, 
  selectedId, 
  keyExtractor, 
  emptyMessage = 'NO DATA AVAILABLE' 
}: DataTableProps<T>) {
  if (data.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500 font-mono text-sm">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="w-full h-full overflow-auto custom-scrollbar bg-gray-950">
      <table className="w-full text-left border-collapse">
        <thead className="sticky top-0 bg-gray-900 shadow-sm z-10">
          <tr>
            {columns.map((col) => (
              <th 
                key={col.key} 
                className={clsx(
                  "p-2 text-xs font-semibold text-gray-400 border-b border-gray-800 whitespace-nowrap",
                  col.width,
                  col.align === 'right' && 'text-right',
                  col.align === 'center' && 'text-center'
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item) => {
            const id = keyExtractor(item);
            const isSelected = selectedId === id;
            return (
              <tr 
                key={id}
                onClick={() => onRowClick?.(item)}
                className={clsx(
                  "border-b border-gray-800/50 hover:bg-gray-800/40 transition-colors h-7",
                  onRowClick && "cursor-pointer",
                  isSelected && "bg-gray-800/60"
                )}
              >
                {columns.map((col) => (
                  <td 
                    key={`${id}-${col.key}`}
                    className={clsx(
                      "p-1.5 px-2 text-xs text-gray-300 whitespace-nowrap overflow-hidden text-ellipsis",
                      col.width,
                      col.align === 'right' && 'text-right',
                      col.align === 'center' && 'text-center'
                    )}
                  >
                    {col.render ? col.render(item) : (item as any)[col.key]}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
