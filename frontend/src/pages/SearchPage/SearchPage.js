import React from 'react';
import './SearchPage.css';

const SearchPage = () => {
  return (
    <section className="search-dev">
      <div className="search-dev__card">
        <div className="search-dev__pulse" />
        <div className="search-dev__icon">🔎</div>
        <h2 className="search-dev__title">Поиск в разработке</h2>
        <p className="search-dev__text">
          Готовим умный поиск по людям, брендам и образам. Скоро можно будет искать по фото и стилю.
        </p>
        <div className="search-dev__chips">
          <span>#поиск_по_фото</span>
          <span>#бренды</span>
          <span>#теги</span>
        </div>
      </div>
    </section>
  );
};

export default SearchPage;
