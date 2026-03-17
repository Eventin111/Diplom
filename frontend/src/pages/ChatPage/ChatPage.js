import React from 'react';
import './ChatPage.css';

const ChatPage = () => {
  return (
    <section className="chat-dev">
      <div className="chat-dev__card">
        <div className="chat-dev__glow" />
        <div className="chat-dev__icon">💬</div>
        <h2 className="chat-dev__title">Чаты в разработке</h2>
        <p className="chat-dev__text">
          Мы собираем быстрый и удобный мессенджер внутри Swipelt. Скоро появятся диалоги, реакции и обмен образами.
        </p>
        <div className="chat-dev__timeline">
          <div className="chat-dev__dot is-active" />
          <div className="chat-dev__dot is-active" />
          <div className="chat-dev__dot" />
        </div>
        <p className="chat-dev__caption">Этап: UX и интеграция</p>
      </div>
    </section>
  );
};

export default ChatPage;
