import http from 'k6/http';
import { sleep } from 'k6';

export default function ()
{
  http.get('http://127.0.0.1:8000/api/v1/client');
  sleep(3);
}