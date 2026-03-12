import React, { useState } from 'react';
import './post.css';

const Post = ({ post, onSwipe, onLike }) => {
  const [showComments, setShowComments] = useState(false);
  const [liked, setLiked] = useState(false);

  const handleLike = () => {
    if (!liked) {
      setLiked(true);
      if (onLike) onLike();
    }
  };

  return (
    <div className="post">
      {/* Изображение одежды */}
      <div className="post-image-container">
        <img 
          src={post.image} 
          alt={post.description}
          className="post-image"
        />
        
        {/* Кнопки действий справа */}
        <div className="post-actions">
          <button 
            className={`action-button ${liked ? 'liked' : ''}`}
            onClick={handleLike}
          >
            ❤️ {post.likes}
          </button>
          <button 
            className="action-button"
            onClick={() => setShowComments(true)}
          >
            💬 {post.comments}
          </button>
          <button className="action-button">
            🔄
          </button>
          <button className="action-button">
            ⭐
          </button>
        </div>
      </div>

      {/* Информация о посте */}
      <div className="post-info">
        <div className="post-user">
          <span className="user-avatar">{post.user.avatar}</span>
          <span className="username">@{post.user.username}</span>
        </div>
        <div className="post-description">
          {post.description}
        </div>
        <div className="post-tags">
          #одежда #мода #{post.user.username}
        </div>
      </div>

      {/* Окно комментариев */}
      {showComments && (
        <div className="comments-modal">
          <div className="comments-header">
            <h3>Комментарии ({post.comments})</h3>
            <button onClick={() => setShowComments(false)}>✕</button>
          </div>
          <div className="comments-list">
            <div className="comment">Классная вещь! 👌</div>
            <div className="comment">Где купить? 🤔</div>
            <div className="comment">Мне нравится! ❤️</div>
          </div>
          <div className="comment-input">
            <input type="text" placeholder="Добавить комментарий..." />
            <button>Отправить</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Post;