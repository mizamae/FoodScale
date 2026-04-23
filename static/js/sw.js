self.addEventListener('push', function(event) {
  //console.log('[Service Worker] Push Received.');
  //console.log(`[Service Worker] Push had this data text: "${event.data.text()}"`);

  const data = JSON.parse(event.data.text());
  const title = data.title;
  const options = {
    body: data.body,
    icon: data.icon,
    badge: data.badge,
    data:JSON.stringify({"redirect":data.redirect,})
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
  //console.log('[Service Worker] Notification click received.');
  event.notification.close();
  const data = JSON.parse(event.notification.data);

  event.waitUntil(
    clients.openWindow(data.redirect)
  );
});