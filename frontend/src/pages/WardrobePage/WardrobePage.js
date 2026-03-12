import React, { useState } from 'react';
import './WardrobePage.css';

const WardrobePage = ({ isEmbedded = false, onBack }) => {
  const [activeCategory, setActiveCategory] = useState('all');

  const wardrobeItems = [
    { 
      id: 1, 
      name: 'Классический костюм', 
      category: 'formal',
      image: 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=300&h=400&fit=crop',
      brand: 'Giorgio Armani',
      color: 'Черный',
      lastWorn: 'Сегодня'
    },
    { 
      id: 2, 
      name: 'Спортивный костюм', 
      category: 'sport',
      image: 'https://images.unsplash.com/photo-1544441893-675973e31985?w=300&h=400&fit=crop',
      brand: 'Nike',
      color: 'Серый',
      lastWorn: 'Вчера'
    },
    { 
      id: 3, 
      name: 'Джинсы и рубашка', 
      category: 'casual',
      image: 'https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=300&h=400&fit=crop',
      brand: 'Zara',
      color: 'Синий',
      lastWorn: '2 дня назад'
    },
    { 
      id: 4, 
      name: 'Вечернее платье', 
      category: 'evening',
      image: 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=300&h=400&fit=crop',
      brand: 'Dolce & Gabbana',
      color: 'Красный',
      lastWorn: '3 дня назад'
    },
    { 
      id: 5, 
      name: 'Кожаная куртка', 
      category: 'outerwear',
      image: 'https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=300&h=400&fit=crop',
      brand: 'AllSaints',
      color: 'Коричневый',
      lastWorn: 'Неделю назад'
    },
    { 
      id: 6, 
      name: 'Повседневный комплект', 
      category: 'casual',
      image: 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=300&h=400&fit=crop',
      brand: 'H&M',
      color: 'Бежевый',
      lastWorn: '2 недели назад'
    },
  ];

  const categories = [
    { id: 'all', name: 'Все', count: wardrobeItems.length },
    { id: 'formal', name: 'Деловая', count: wardrobeItems.filter(item => item.category === 'formal').length },
    { id: 'casual', name: 'Повседневная', count: wardrobeItems.filter(item => item.category === 'casual').length },
    { id: 'sport', name: 'Спортивная', count: wardrobeItems.filter(item => item.category === 'sport').length },
    { id: 'evening', name: 'Вечерняя', count: wardrobeItems.filter(item => item.category === 'evening').length },
    { id: 'outerwear', name: 'Верхняя одежда', count: wardrobeItems.filter(item => item.category === 'outerwear').length },
  ];

  const filteredItems = activeCategory === 'all' 
    ? wardrobeItems 
    : wardrobeItems.filter(item => item.category === activeCategory);

  return (
    <div className="wardrobe-container">
      <header className="wardrobe-header">
        <button className="back-btn" onClick={onBack}>
          ← Назад
        </button>
        <h1 className="wardrobe-title">Мой гардероб</h1>
        <button className="add-item-btn">+</button>
      </header>

      <div className="wardrobe-content">
        {/* Категории */}
        <div className="categories-section">
          <div className="categories-scroll">
            {categories.map(category => (
              <button
                key={category.id}
                className={`category-btn ${activeCategory === category.id ? 'active' : ''}`}
                onClick={() => setActiveCategory(category.id)}
              >
                <span className="category-name">{category.name}</span>
                <span className="category-count">{category.count}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Сетка одежды */}
        <div className="wardrobe-grid">
          {filteredItems.map(item => (
            <div key={item.id} className="wardrobe-item">
              <img src={item.image} alt={item.name} className="item-image" />
              <div className="item-info">
                <h4 className="item-name">{item.name}</h4>
                <div className="item-details">
                  <span className="item-brand">{item.brand}</span>
                  <span className="item-color">{item.color}</span>
                </div>
                <div className="item-footer">
                  <span className="item-last-worn">Надето: {item.lastWorn}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WardrobePage;