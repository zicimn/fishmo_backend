import request from './request'

export interface PostRequest {
  status?: boolean
  title: string
  category: string
  content: string
  images?: string[]
}

export interface ArticleEditRequest {
  status: boolean
  title?: string
  category?: string
  content?: string
  images?: string[]
}

export interface ArticleItem {
  id: number
  title: string
  author_name: string
  category: string
  views: number
  likes: number
  create_at: string
  avatar?: string | null
}

export interface ArticleListResponse {
  total: number
  items: ArticleItem[]
}

export interface ArticleDetailResponse {
  title: string
  content: string
  images: string[]
  author_id: number
  author_name: string
  author_avatar: string
  views: number
  category?: string
  created_at?: string
  id?: number
}

export interface UserArticleItem {
  id: number
  title: string
  category: string
  content: string
  views: number
  likes: number
  created_at: string
}

export interface UserArticlesResponse {
  author_id: number
  articles: UserArticleItem[]
}

export interface LinkRequest {
  url: string
  title?: string
}

export interface LinkResponse {
  id: number
  url: string
  title?: string
  article_id: number
}

export interface HomeArticleItem {
  id: number
  title: string
  category: string
  views: number
  likes: number
  created_at: string
}

export interface HomeArticlesResponse {
  author_id: number
  articles: HomeArticleItem[]
}

export interface HomeCommentItem {
  article_id: number
  content: string
  created_at: string
}

export interface HomeCommentsResponse {
  comments: HomeCommentItem[]
}

export interface CommentRequest {
  content: string
}

export interface CommentResponse {
  id: number
  content: string
  name: string
  created_at: string
}

export const articleApi = {
  publish: (data: PostRequest) => request.post('/article/publish/', data),
  visit: (id: number) => request.get<ArticleDetailResponse>(`/article/visit/${id}`),
  list: (page: number = 1, size: number = 10, category?: string, sort: string = 'created_at', order: string = 'desc') => request.get<ArticleListResponse>('/article/', { params: { page, size, category, sort, order } }),
  edit: (id: number, data: ArticleEditRequest) => request.put(`/article/edit/${id}`, data),
  getUserArticles: (page: number = 1, size: number = 10) => request.get<UserArticlesResponse>('/user/article/get_list', { params: { page, size } }),
  deleteArticle: (id: number) => request.delete(`/article/delete/${id}`, { params: { ok: true } }),
  submitLink: (articleId: number, data: LinkRequest) => request.post(`/article/${articleId}/submit_link`, data),
  getLinks: (articleId: number, page: number = 1, size: number = 10) => request.get<{ links: LinkResponse[] }>(`/article/${articleId}/links`, { params: { page, size } }),
  getLink: (articleId: number, linkId: number) => request.get<LinkResponse>(`/article/${articleId}/links/${linkId}`),
  deleteLink: (articleId: number, linkId: number) => request.delete(`/article/${articleId}/deleted/${linkId}`, { params: { ok: true } }),
  getUserLinks: (page: number = 1, size: number = 10) => request.get<{ links: LinkResponse[] }>('/user/article/getlinklist', { params: { page, size } }),
  deleteUserLink: (articleId: number, linkId: number) => request.delete(`/article/${articleId}/deleted/${linkId}`, { params: { ok: true } }),
  getHomeArticles: (userId: number, page: number = 1, size: number = 10) => request.get<HomeArticlesResponse>(`/home/article/${userId}`, { params: { page, size } }),
  getHomeComments: (userId: number, page: number = 1, size: number = 10) => request.get<HomeCommentsResponse>(`/home/comment/${userId}`, { params: { page, size } }),
  getComments: (articleId: number) => request.get<{ msg: string; comments: CommentResponse[] }>(`/article/${articleId}/comment`),
  submitComment: (articleId: number, data: CommentRequest) => request.post(`/article/${articleId}/comments`, null, { params: { content: data.content } }),
  deleteComment: (id: number) => request.delete(`/article/commment/remove/${id}`),
  addFavorite: (articleId: number) => request.post(`/article/favorite/add/${articleId}`),
  removeFavorite: (articleId: number) => request.delete(`/article/favorite/remove/${articleId}`)
}
