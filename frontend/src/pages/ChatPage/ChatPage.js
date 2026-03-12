import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './ChatPage.css';

const ChatPage = ({ isEmbedded = false }) => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const [chats, setChats] = useState([
    {
      id: 1,
      user: {
        name: 'Алексей',
        username: '@alex_style',
        avatar: 'https://ui-avatars.com/api/?name=Алексей&background=ff0000&color=fff',
        isOnline: true
      },
      lastMessage: 'Привет! Как тебе мой новый костюм?',
      timestamp: '10:30',
      unreadCount: 2,
      isTyping: false
    },
    {
      id: 2,
      user: {
        name: 'Мария',
        username: '@mari_fashion',
        avatar: 'https://ui-avatars.com/api/?name=Мария&background=ff3333&color=fff',
        isOnline: true
      },
      lastMessage: 'Спасибо за лайк! ❤️',
      timestamp: 'Вчера',
      unreadCount: 0,
      isTyping: true
    }
  ]);

  const [activeChat, setActiveChat] = useState(null);
  const [messageInput, setMessageInput] = useState('');
  const [messages, setMessages] = useState({});
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const initialMessages = {
      1: [
        { id: 1, text: 'Привет! Как тебе мой новый костюм?', sender: 'them', timestamp: '10:30' },
        { id: 2, text: 'Очень стильно! Где покупал?', sender: 'me', timestamp: '10:32' },
        { id: 3, text: 'В бутике Giorgio Armani', sender: 'them', timestamp: '10:33' },
        { id: 4, text: 'Выглядит дорого!', sender: 'me', timestamp: '10:35' },
        { id: 5, text: 'Спасибо!', sender: 'them', timestamp: '10:36' },
      ],
      2: [
        { id: 1, text: 'Спасибо за лайк! ❤️', sender: 'them', timestamp: 'Вчера 15:20' },
        { id: 2, text: 'Не за что! Твое платье просто потрясающее!', sender: 'me', timestamp: 'Вчера 15:22' },
        { id: 3, text: 'Спасибо! Оно из новой коллекции D&G...', sender: 'them', timestamp: 'Сейчас' },
      ]
    };
    setMessages(initialMessages);
  }, []);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    if (activeChat) {
      setTimeout(scrollToBottom, 100);
    }
  }, [activeChat, messages]);

  useEffect(() => {
    if (!isAuthenticated && !isEmbedded) {
      navigate('/login');
      return;
    }
    
    if (user?.isGuest) {
      if (isEmbedded) {
        return;
      } else {
        navigate('/');
      }
    }
  }, [isAuthenticated, navigate, isEmbedded, user?.isGuest]);

  const handleChatSelect = (chatId) => {
    if (user?.isGuest) return;
    setActiveChat(chatId);
    setChats(prevChats => 
      prevChats.map(chat => 
        chat.id === chatId ? { ...chat, unreadCount: 0 } : chat
      )
    );
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    
    if (user?.isGuest || !messageInput.trim() || !activeChat) return;

    const newMessage = {
      id: Date.now(),
      text: messageInput,
      sender: 'me',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => ({
      ...prev,
      [activeChat]: [...(prev[activeChat] || []), newMessage]
    }));

    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === activeChat
          ? { ...chat, lastMessage: messageInput, timestamp: 'Только что' }
          : chat
      )
    );

    setMessageInput('');

    setTimeout(() => {
      const botMessage = {
        id: Date.now() + 1,
        text: 'Спасибо за сообщение! Я отвечу позже.',
        sender: 'them',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => ({
        ...prev,
        [activeChat]: [...(prev[activeChat] || []), botMessage]
      }));

      setTimeout(scrollToBottom, 100);
    }, 1000);
  };

  const handleBackToChats = () => {
    setActiveChat(null);
  };

  const handleNewChat = () => {
    if (user?.isGuest) return;
    
    const newChatId = Date.now();
    const newChat = {
      id: newChatId,
      user: {
        name: 'Новый пользователь',
        username: '@new_user',
        avatar: 'https://ui-avatars.com/api/?name=Пользователь&background=666666&color=fff',
        isOnline: true
      },
      lastMessage: '',
      timestamp: 'Сейчас',
      unreadCount: 0,
      isTyping: false
    };
    
    setChats(prev => [newChat, ...prev]);
    setActiveChat(newChatId);
  };

  if (user?.isGuest) {
    return (
      <div className="chat-container">
        <header className="chat-header list-mode">
          <h1 className="chat-title">Сообщения</h1>
        </header>
        <div className="guest-chats-info">
          <div className="guest-chats-icon-large">💬</div>
          <h3>Чаты недоступны</h3>
          <p>Для доступа к чатам войдите или зарегистрируйтесь</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated && !isEmbedded) {
    return null;
  }

  return (
    <div className="chat-container">
      {activeChat ? (
        // ОТКРЫТЫЙ ЧАТ
        <>
          {/* Шапка открытого чата С КНОПКОЙ НАЗАД */}
          <header className="chat-header chat-mode">
            <button 
              className="chat-back-btn" 
              onClick={handleBackToChats}
              title="Назад к чатам"
            >
              ←
            </button>
            
            {(() => {
              const chat = chats.find(c => c.id === activeChat);
              return chat ? (
                <div className="chat-partner-info">
                  <img src={chat.user.avatar} alt={chat.user.name} className="partner-avatar" />
                  <div className="partner-details">
                    <h3 className="partner-name">{chat.user.name}</h3>
                    <p className="partner-status">
                      {chat.user.isOnline ? (
                        <span className="online-status">● онлайн</span>
                      ) : (
                        <span className="offline-status">был(а) недавно</span>
                      )}
                    </p>
                  </div>
                </div>
              ) : null;
            })()}
          </header>

          {/* Сообщения */}
          <div className="chat-window">
            <div className="messages-container">
              <div className="messages-list">
                {messages[activeChat]?.map((message) => (
                  <div
                    key={message.id}
                    className={`message ${message.sender === 'me' ? 'message-sent' : 'message-received'}`}
                  >
                    <div className="message-content">
                      <p className="message-text">{message.text}</p>
                      <span className="message-time">{message.timestamp}</span>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </div>
          </div>

          {/* ПОЛЕ ВВОДА С НОВЫМ ДИЗАЙНОМ */}
          <div className="chat-input-container">
            <form className="message-input-wrapper" onSubmit={handleSendMessage}>
              <input
                type="text"
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                placeholder="Напишите сообщение..."
                className="message-input"
                autoFocus
              />
              <button 
                type="submit" 
                className="send-button" 
                disabled={!messageInput.trim()}
                title="Отправить"
              >
                →
              </button>
            </form>
          </div>
        </>
      ) : (
        // СПИСОК ЧАТОВ
        <>
          <header className="chat-header list-mode">
            <div style={{ width: '40px' }}></div>
            <h1 className="chat-title">Сообщения</h1>
            <button 
              className="new-chat-btn" 
              title="Новый чат" 
              onClick={handleNewChat}
            >
              +
            </button>
          </header>

          <div className="chats-list">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className={`chat-item ${chat.unreadCount > 0 ? 'unread' : ''}`}
                onClick={() => handleChatSelect(chat.id)}
              >
                <div className="chat-avatar-container">
                  <img src={chat.user.avatar} alt={chat.user.name} className="chat-avatar" />
                  {chat.user.isOnline && <span className="online-dot"></span>}
                </div>
                
                <div className="chat-info">
                  <h4 className="chat-user-name">{chat.user.name}</h4>
                  <div className="chat-preview">
                    <p className="chat-last-message">
                      {chat.isTyping ? (
                        <span className="typing-indicator">печатает...</span>
                      ) : (
                        chat.lastMessage
                      )}
                    </p>
                    <span className="chat-time">{chat.timestamp}</span>
                    {chat.unreadCount > 0 && (
                      <span className="unread-badge">{chat.unreadCount}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {chats.length === 0 && (
              <div className="empty-chats">
                <div className="empty-chats-icon">💬</div>
                <h3>Нет сообщений</h3>
                <p>Начните общение с другими пользователями</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default ChatPage;