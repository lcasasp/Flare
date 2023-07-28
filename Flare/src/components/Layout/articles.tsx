import React from 'react';

interface Article {
  id: number;
  title: string;
  content: string;
  url: string;
  date: string;
}

interface ArticlesProps {
  articles: Article[];
}

const Articles: React.FC<ArticlesProps> = ({ articles }) => {
  return (
    <div>
      <h2 style={{display: 'flex', justifyContent: 'center', alignItems: 'center', paddingBottom: '20px'}}><b>News Articles</b></h2>
      {articles.length > 0 ? (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {articles.map((article) => (
            <li key={article.id} style={{ border: '1px solid gray', borderRadius: '4px', padding: '10px', marginBottom: '10px' }}>
              <a href={article.url} target='_blank' rel='noreferrer noopener' style={{ textDecoration: 'underline', color: 'black' }} >
                <h3>{article.title}</h3>
                <p>Published At: {new Date(article.date).toLocaleString()}</p>
              </a>
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
