import React, { useState } from 'react';
import { Search, Filter, X } from 'lucide-react';
import { useUIStore } from '../../stores/uiStore';

interface FilterBarProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  filters?: React.ReactNode;
}

export const FilterBar: React.FC<FilterBarProps> = ({ placeholder = 'Search...', onSearch, filters }) => {
  const [query, setQuery] = useState('');
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch(query);
    }
  };

  const handleClear = () => {
    setQuery('');
    onSearch('');
  };

  return (
    <div className={`h-12 flex items-center px-4 gap-4 shrink-0 border-b mb-4 ${isDark ? 'bg-[#0A0A0A] border-[#333]' : 'bg-white border-slate-200 shadow-sm rounded-xl'}`}>
      <div className={`flex-1 flex items-center rounded-md px-3 h-8 transition-colors ${
        isDark ? 'bg-[#111] border border-[#333] focus-within:border-rose-500' : 'bg-slate-50 border border-slate-200 focus-within:border-[#00bceb] focus-within:ring-2 focus-within:ring-[#00bceb]/20'
      }`}>
        <Search size={14} className={isDark ? 'text-gray-500 mr-2' : 'text-slate-400 mr-2'} />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={`flex-1 bg-transparent border-none outline-none text-sm ${
            isDark ? 'text-gray-100 font-mono placeholder-gray-600' : 'text-slate-700 font-sans placeholder-slate-400'
          }`}
          spellCheck={false}
        />
        {query && (
          <button onClick={handleClear} className={`hover:text-gray-300 ${isDark ? 'text-gray-500' : 'text-slate-400'}`}>
            <X size={14} />
          </button>
        )}
      </div>
      {filters && (
        <div className={`flex items-center gap-2 pl-4 border-l ${isDark ? 'border-[#333]' : 'border-slate-200'}`}>
          <Filter size={14} className={isDark ? 'text-gray-500' : 'text-slate-400'} />
          {filters}
        </div>
      )}
    </div>
  );
};
