import React from 'react';
import clsx from 'clsx';
import { useUIStore } from '../../stores/uiStore';

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
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  if (data.length === 0) {
    return (
      <div className={`flex-1 flex items-center justify-center text-sm ${isDark ? 'text-gray-500 font-mono' : 'text-slate-400 font-sans'}`}>
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className={`w-full h-full overflow-auto custom-scrollbar transition-all duration-300 ${isDark ? 'bg-[#000]' : 'bg-white/70 backdrop-blur-md rounded-2xl shadow-sm border border-slate-200/60'}`}>
      <table className="w-full text-left whitespace-nowrap">
        <thead className={`sticky top-0 z-10 ${isDark ? 'bg-[#111] border-b border-[#333]' : 'bg-slate-50/80 backdrop-blur-sm border-b border-slate-100/60'}`}>
          <tr>
            {columns.map((col) => (
              <th 
                key={col.key} 
                className={clsx(
                  "px-4 py-3 text-xs font-semibold uppercase tracking-wider",
                  isDark ? "text-[#666]" : "text-slate-400",
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
        <tbody className={`divide-y ${isDark ? 'divide-[#222]' : 'divide-slate-50/50'}`}>
          {data.map((item, idx) => {
            const id = keyExtractor(item);
            const isSelected = selectedId === id;
            return (
              <tr 
                key={id}
                onClick={() => onRowClick?.(item)}
                className={clsx(
                  "transition-all duration-200",
                  isDark 
                    ? (isSelected ? "bg-[#1A1A1A] border-l-2 border-blue-500" : "border-l-2 border-transparent hover:bg-[#111]")
                    : (isSelected ? "bg-indigo-50/60 shadow-sm rounded-xl scale-[0.995]" : "hover:bg-slate-50 rounded-xl"),
                  onRowClick && "cursor-pointer"
                )}
              >
                {columns.map((col, cIdx) => (
                  <td 
                    key={`${id}-${col.key}`}
                    className={clsx(
                      "px-4 py-3.5 text-sm overflow-hidden text-ellipsis",
                      isDark ? "text-gray-300" : "text-slate-700 font-medium",
                      cIdx === 0 && !isDark ? "rounded-l-xl" : "",
                      cIdx === columns.length - 1 && !isDark ? "rounded-r-xl" : "",
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
