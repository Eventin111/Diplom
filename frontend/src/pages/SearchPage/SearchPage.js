import React, { useState } from 'react';
import './SearchPage.css';

const SearchPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  // Моковые данные для поиска
  const mockResults = [
    { id: 1, type: 'user', name: 'Алексей', username: '@alex_style', avatar: 'https://ui-avatars.com/api/?name=Алексей&background=ff0000&color=fff' },
    { id: 2, type: 'user', name: 'Мария', username: '@mari_fashion', avatar: 'https://ui-avatars.com/api/?name=Мария&background=ff3333&color=fff' },
    { id: 3, type: 'tag', name: '#костюм', count: 1245 },
    { id: 4, type: 'tag', name: '#платье', count: 876 },
    { id: 5, type: 'brand', name: 'Giorgio Armani', count: 234 },
    { id: 6, type: 'brand', name: 'Dolce & Gabbana', count: 189 },
  ];

  const handleSearch = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    
    if (query.trim() === '') {
      setSearchResults([]);
    } else {
      // Фильтруем результаты по запросу
      const filtered = mockResults.filter(item => 
        item.name.toLowerCase().includes(query.toLowerCase()) ||
        (item.username && item.username.toLowerCase().includes(query.toLowerCase()))
      );
      setSearchResults(filtered);
    }
  };

  const handleResultClick = (result) => {
    console.log('Clicked:', result);
    // В будущем переход к результату поиска
  };

  return (
    <div className="search-container">
      <div className="search-header">
        <h1 className="search-title">Поиск</h1>
        <p className="search-subtitle">Найдите пользователей, теги и бренды</p>
      </div>

      <div className="search-input-container">
        <input
          type="text"
          value={searchQuery}
          onChange={handleSearch}
          placeholder="Введите запрос..."
          className="search-input"
        />
        <span className="search-icon">🔍</span>
      </div>

      {searchResults.length > 0 ? (
        <div className="search-results">
          {searchResults.map((result) => (
            <div 
              key={result.id} 
              className="search-result-item"
              onClick={() => handleResultClick(result)}
            >
              {result.type === 'user' && (
                <>
                  <img src={result.avatar} alt={result.name} className="result-avatar" />
                  <div className="result-info">
                    <div className="result-name">{result.name}</div>
                    <div className="result-username">{result.username}</div>
                  </div>
                  <button className="follow-result-btn">Подписаться</button>
                </>
              )}
              {result.type === 'tag' && (
                <>
                  <span className="result-icon">🏷️</span>
                  <div className="result-info">
                    <div className="result-name">{result.name}</div>
                    <div className="result-count">{result.count} постов</div>
                  </div>
                </>
              )}
              {result.type === 'brand' && (
                <>
                  <span className="result-icon">👔</span>
                  <div className="result-info">
                    <div className="result-name">{result.name}</div>
                    <div className="result-count">{result.count} примерок</div>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      ) : searchQuery.trim() !== '' ? (
        <div className="no-results">
          <span className="no-results-icon">🔍</span>
          <p className="no-results-text">Ничего не найдено</p>
          <p className="no-results-subtext">Попробуйте другой запрос</p>
        </div>
      ) : (
        <div className="search-trends">
          <h3 className="trends-title">Популярные запросы</h3>
          <div className="trends-grid">
            {mockResults.map((trend) => (
              <div 
                key={trend.id} 
                className="trend-item"
                onClick={() => {
                  setSearchQuery(trend.name);
                  setSearchResults([trend]);
                }}
              >
                {trend.type === 'user' ? '👤' : trend.type === 'tag' ? '🏷️' : '👔'}
                <span className="trend-name">{trend.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPage;