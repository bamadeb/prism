import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
@Injectable({ providedIn: 'root' })
export class ApiService {
  base = '/api'; // with proxy
  constructor(private http: HttpClient) {}
  health() { return this.http.get(`${this.base}/health`); }
  listPatients(){ return this.http.get(`${this.base}/patients`); }
  createPatient(p:any){ return this.http.post(`${this.base}/patients`, p); }
}
