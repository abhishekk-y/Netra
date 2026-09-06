import React, { useState } from 'react';
import { Search, Filter, X } from 'lucide-react';

interface FilterBarProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  filters?: React.ReactNode;
}

export const FilterBar: React.FC<FilterBarProps> = ({ placeholder = 'Search...', onSearch, filters }) => {
  const [query, setQuery] = useState('');

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
    <div className="h-10 bg-gray-900 border-b border-gray-800 flex items-center px-2 gap-2 shrink-0">
      <div className="flex-1 flex items-center bg-gray-950 border border-gray-800 rounded px-2 h-7 focus-within:border-emerald-500/50 transition-colors">
        <Search size={14} className="text-gray-500 mr-2" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 bg-transparent border-none outline-none text-sm text-gray-100 font-mono placeholder-gray-600"
          spellCheck={false}
        />
        {query && (
          <button onClick={handleClear} className="text-gray-500 hover:text-gray-300">
            <X size={14} />
          </button>
        )}
      </div>
      {filters && (
        <div className="flex items-center gap-2 border-l border-gray-800 pl-2">
          <Filter size={14} className="text-gray-500" />
          {filters}
        </div>
      )}
    </div>
  );
};
