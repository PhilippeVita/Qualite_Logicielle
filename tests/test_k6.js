import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 50, // 50 utilisateurs simultanés
  duration: '30s' // pendant 30 secondes
};

export default function () {
  // 1. GET - Lire tous les clients
  http.get('http://127.0.0.1:8000/api/v1/client/');

  // 2. POST - Créer un nouveau client
  const newClient = JSON.stringify({
    nom: 'Durand',
    prenom: 'Alice',
    genre: 'F',
    adresse: '12 rue des Lilas',
    complement_adresse: 'Bâtiment B',
    tel: '0601020304',
    email: `alice${__VU}_${__ITER}@example.com`,
    newsletter: 1
  });

  const headers = { 'Content-Type': 'application/json' };
  const postRes = http.post('http://127.0.0.1:8000/api/v1/client/', newClient, { headers });

  // 3. Extraire l'ID du client créé
  let client_id;
  try {
    client_id = JSON.parse(postRes.body).codcli;
  } catch (e) {
    console.error('Erreur de parsing POST:', e);
    return;
  }

  // 4. PATCH - Modifier le prénom du client
  const patchBody = JSON.stringify({ prenom: 'Alicia' });
  http.patch(`http://127.0.0.1:8000/api/v1/client/${client_id}`, patchBody, { headers });

  // 5. DELETE - Supprimer le client
  http.del(`http://127.0.0.1:8000/api/v1/client/${client_id}`);

  sleep(1);
}
