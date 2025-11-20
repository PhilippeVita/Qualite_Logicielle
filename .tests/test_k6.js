import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 10, // Nombre d'utilisateurs virtuels simultanés
  duration: '10s' // Durée totale du test
};

export default function () {
  http.get('http://127.0.0.1:8000/api/v1/client');
  sleep(1); // Pause entre les requêtes
}
