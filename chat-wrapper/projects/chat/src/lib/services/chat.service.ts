import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ChatService {

  constructor(private readonly http: HttpClient) { }

  uploadDocument(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post('http://localhost:5555/upload', formData);
  }

  askQuestion(question: string) {
    return this.http.post('http://localhost:5555/query', { question: question });
  }
}
