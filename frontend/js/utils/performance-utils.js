// 前端性能优化工具集
// File: /home/qw/.openclaw/workspace/VehicleTestAI1/frontend/js/utils/performance-utils.js
// Purpose: 防抖、节流、懒加载、虚拟滚动等性能优化工具

(function() {
    'use strict';
    
    // ==================== 防抖函数 ====================
    
    function debounce(func, wait, immediate = false) {
        let timeout;
        
        return function executedFunction(...args) {
            const context = this;
            
            const later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            
            const callNow = immediate && !timeout;
            
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            
            if (callNow) func.apply(context, args);
        };
    }
    
    // ==================== 节流函数 ====================
    
    function throttle(func, limit) {
        let inThrottle;
        
        return function(...args) {
            const context = this;
            
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    // ==================== 懒加载 ====================
    
    class LazyLoader {
        constructor(options = {}) {
            this.root = options.root || null;
            this.rootMargin = options.rootMargin || '50px';
            this.threshold = options.threshold || 0.1;
            this.observer = null;
            this.elements = new Map();
            
            this.init();
        }
        
        init() {
            if ('IntersectionObserver' in window) {
                this.observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.loadElement(entry.target);
                        }
                    });
                }, {
                    root: this.root,
                    rootMargin: this.rootMargin,
                    threshold: this.threshold
                });
            }
        }
        
        observe(element, callback) {
            if (this.observer) {
                this.elements.set(element, callback);
                this.observer.observe(element);
            } else {
                // 降级：直接加载
                callback(element);
            }
        }
        
        unobserve(element) {
            if (this.observer) {
                this.observer.unobserve(element);
                this.elements.delete(element);
            }
        }
        
        loadElement(element) {
            const callback = this.elements.get(element);
            if (callback) {
                callback(element);
                this.unobserve(element);
            }
        }
        
        destroy() {
            if (this.observer) {
                this.observer.disconnect();
            }
            this.elements.clear();
        }
    }
    
    // 全局懒加载实例
    const lazyLoader = new LazyLoader();
    
    // ==================== 虚拟滚动 ====================
    
    class VirtualScroller {
        constructor(container, options = {}) {
            this.container = container;
            this.itemHeight = options.itemHeight || 50;
            this.buffer = options.buffer || 5;
            this.items = [];
            this.visibleItems = [];
            
            this.init();
        }
        
        init() {
            // 创建视口容器
            this.viewport = document.createElement('div');
            this.viewport.style.cssText = `
                height: 100%;
                overflow-y: auto;
                position: relative;
            `;
            
            // 创建内容容器
            this.content = document.createElement('div');
            this.content.style.cssText = `
                position: relative;
            `;
            
            this.viewport.appendChild(this.content);
            this.container.appendChild(this.viewport);
            
            // 监听滚动
            this.viewport.addEventListener('scroll', throttle(() => {
                this.render();
            }, 16)); // ~60fps
        }
        
        setItems(items) {
            this.items = items;
            this.content.style.height = `${items.length * this.itemHeight}px`;
            this.render();
        }
        
        render() {
            const scrollTop = this.viewport.scrollTop;
            const viewportHeight = this.viewport.clientHeight;
            
            const startIndex = Math.max(0, Math.floor(scrollTop / this.itemHeight) - this.buffer);
            const endIndex = Math.min(
                this.items.length,
                Math.ceil((scrollTop + viewportHeight) / this.itemHeight) + this.buffer
            );
            
            // 清空内容
            this.content.innerHTML = '';
            
            // 渲染可见项
            for (let i = startIndex; i < endIndex; i++) {
                const item = this.items[i];
                const element = this.renderItem(item, i);
                
                element.style.cssText = `
                    position: absolute;
                    top: ${i * this.itemHeight}px;
                    width: 100%;
                    height: ${this.itemHeight}px;
                `;
                
                this.content.appendChild(element);
            }
        }
        
        renderItem(item, index) {
            // 由子类实现
            const div = document.createElement('div');
            div.textContent = item.name || `Item ${index}`;
            return div;
        }
        
        scrollToIndex(index) {
            this.viewport.scrollTop = index * this.itemHeight;
        }
    }
    
    // ==================== 资源预加载 ====================
    
    class ResourcePreloader {
        static preloadImage(url) {
            return new Promise((resolve, reject) => {
                const img = new Image();
                img.onload = () => resolve(img);
                img.onerror = reject;
                img.src = url;
            });
        }
        
        static preloadImages(urls) {
            return Promise.all(urls.map(url => this.preloadImage(url)));
        }
        
        static prefetch(url) {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = url;
            document.head.appendChild(link);
        }
        
        static preload(url, as = 'script') {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = as;
            link.href = url;
            document.head.appendChild(link);
        }
    }
    
    // ==================== 性能监控 ====================
    
    class PerformanceMonitor {
        constructor() {
            this.metrics = {
                fps: [],
                memory: [],
                timing: {}
            };
            
            this.init();
        }
        
        init() {
            // 记录页面加载性能
            if (window.performance) {
                window.addEventListener('load', () => {
                    setTimeout(() => {
                        const timing = performance.timing;
                        this.metrics.timing = {
                            dns: timing.domainLookupEnd - timing.domainLookupStart,
                            tcp: timing.connectEnd - timing.connectStart,
                            request: timing.responseStart - timing.requestStart,
                            response: timing.responseEnd - timing.responseStart,
                            dom: timing.domComplete - timing.domLoading,
                            total: timing.loadEventEnd - timing.navigationStart
                        };
                        
                        console.log('📊 页面加载性能:', this.metrics.timing);
                    }, 0);
                });
            }
            
            // 监控 FPS
            this.monitorFPS();
        }
        
        monitorFPS() {
            let lastTime = performance.now();
            let frames = 0;
            
            const measure = () => {
                frames++;
                const currentTime = performance.now();
                
                if (currentTime >= lastTime + 1000) {
                    const fps = Math.round((frames * 1000) / (currentTime - lastTime));
                    this.metrics.fps.push(fps);
                    
                    // 只保留最近 60 个值
                    if (this.metrics.fps.length > 60) {
                        this.metrics.fps.shift();
                    }
                    
                    frames = 0;
                    lastTime = currentTime;
                }
                
                requestAnimationFrame(measure);
            };
            
            requestAnimationFrame(measure);
        }
        
        getStats() {
            const avgFps = this.metrics.fps.length > 0
                ? Math.round(this.metrics.fps.reduce((a, b) => a + b) / this.metrics.fps.length)
                : 0;
            
            return {
                fps: {
                    current: this.metrics.fps[this.metrics.fps.length - 1] || 0,
                    average: avgFps,
                    min: Math.min(...this.metrics.fps) || 0,
                    max: Math.max(...this.metrics.fps) || 0
                },
                timing: this.metrics.timing
            };
        }
    }
    
    // 全局性能监控器
    const performanceMonitor = new PerformanceMonitor();
    
    // ==================== 本地存储优化 ====================
    
    class StorageOptimizer {
        static set(key, value, ttl = null) {
            const item = {
                value: value,
                expiry: ttl ? Date.now() + ttl * 1000 : null
            };
            
            try {
                localStorage.setItem(key, JSON.stringify(item));
            } catch (e) {
                // 存储空间满了，清理过期数据
                this.cleanup();
                localStorage.setItem(key, JSON.stringify(item));
            }
        }
        
        static get(key) {
            try {
                const itemStr = localStorage.getItem(key);
                if (!itemStr) return null;
                
                const item = JSON.parse(itemStr);
                
                // 检查是否过期
                if (item.expiry && Date.now() > item.expiry) {
                    localStorage.removeItem(key);
                    return null;
                }
                
                return item.value;
            } catch (e) {
                return null;
            }
        }
        
        static remove(key) {
            localStorage.removeItem(key);
        }
        
        static cleanup() {
            const keys = Object.keys(localStorage);
            
            keys.forEach(key => {
                try {
                    const item = JSON.parse(localStorage.getItem(key));
                    if (item.expiry && Date.now() > item.expiry) {
                        localStorage.removeItem(key);
                    }
                } catch (e) {
                    // 不是 JSON，跳过
                }
            });
        }
    }
    
    // ==================== 导出全局函数 ====================
    
    window.PerformanceUtils = {
        debounce: debounce,
        throttle: throttle,
        LazyLoader: LazyLoader,
        VirtualScroller: VirtualScroller,
        ResourcePreloader: ResourcePreloader,
        PerformanceMonitor: PerformanceMonitor,
        StorageOptimizer: StorageOptimizer,
        
        // 便捷方法
        lazyLoader: lazyLoader,
        performanceMonitor: performanceMonitor,
        
        getStats: () => performanceMonitor.getStats()
    };
    
    console.log('✅ 性能优化工具已加载');
    
})();
