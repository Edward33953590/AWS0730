/* Service Worker for 优惠券中心 */
const CACHE_NAME = 'coupon-center-v1';

// 预缓存的核心页面
const PRECACHE_URLS = [
    '/',
    '/auth/login',
    '/user/coupons',
    '/verifier',
    '/verifier/records'
];

// 安装时预缓存核心页面
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// 激活时清理旧缓存
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.filter(name => name !== CACHE_NAME)
                    .map(name => caches.delete(name))
            );
        }).then(() => self.clients.claim())
    );
});

// 网络优先策略（先请求网络，失败时用缓存）
self.addEventListener('fetch', event => {
    // 只缓存 GET 请求
    if (event.request.method !== 'GET') return;

    // API 请求不缓存（保证数据实时性）
    if (event.request.url.includes('/api/')) return;

    event.respondWith(
        fetch(event.request)
            .then(response => {
                // 缓存成功的响应
                if (response.status === 200) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, clone);
                    });
                }
                return response;
            })
            .catch(() => {
                // 网络失败时从缓存中获取
                return caches.match(event.request).then(cached => {
                    return cached || new Response('离线模式 - 请检查网络连接', {
                        status: 408,
                        statusText: 'Offline'
                    });
                });
            })
    );
});
