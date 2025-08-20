// static/js/burger_animation.js
document.addEventListener('DOMContentLoaded', () => {
    const layerIds = [
        'bottom-bun', 
        'patty', 
        'cheese', 
        'lettuce', 
        'tomato', 
        'top-bun'
    ];
    
    const layers = layerIds.map(id => document.getElementById(id)).filter(layer => layer !== null); 

    function animateBurger() {
        layers.forEach(layer => {
            layer.classList.remove('visible');
        });

        const animationStartDelay = 100; 
        setTimeout(() => {
            let currentLayerDisplayDelay = 0; 
        
            layers.forEach((layer) => {
                setTimeout(() => {
                    if (layer) { 
                        layer.classList.add('visible');
                    }
                }, currentLayerDisplayDelay);
                currentLayerDisplayDelay += 450; 
            });
        }, animationStartDelay);
    }

    setTimeout(animateBurger, 700);
});