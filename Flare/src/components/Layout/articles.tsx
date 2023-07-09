import React from 'react';

interface Article {
  id: number;
  title: string;
  content: string;
}

interface ArticlesProps {
  articles: Article[];
}

const Articles: React.FC<ArticlesProps> = ({ articles }) => {
  return (
    <div>
      <h2 style={{display: 'flex', justifyContent: 'center', alignItems: 'center', paddingBottom: '20px'}}><b>News Articles</b></h2>
      {articles.length > 0 ? (
        <ul>
          {articles.map((article) => (
            <li key={article.id}>
              <h3>{article.title}</h3>
              <p>{article.content}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>No articles found.</p>
      )}
    </div>
  );
};

export default Articles;
