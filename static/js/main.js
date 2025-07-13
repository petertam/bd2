document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const chatBox = document.getElementById('chat-box');
    const personalityList = document.getElementById('personality-list');
    const currentPersonalityName = document.getElementById('current-personality-name');
    
    let currentPersonality = 'Warren Buffett';
    
    // Input history management
    let inputHistory = [];
    let historyIndex = -1;
    const MAX_HISTORY = 10;
    
    // Function to add message to chat
    function addMessage(message, sender = 'bot', personality = null, data = null) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        
        let messageContent = '';
        
        if (sender === 'bot' && personality) {
            messageContent += `<div class="message-personality">${personality}</div>`;
        }
        
        // Format trading advice if it contains recommendations
        if (sender === 'bot' && message.includes('**RECOMMENDATION:') && message.includes('**CONFIDENCE SCORE:')) {
            messageContent += `<div class="message-text">${formatTradingAdvice(message)}</div>`;
        } else {
            messageContent += `<div class="message-text">${message}</div>`;
        }
        
        // Add stock data if available
        if (data && data.stock_data) {
            messageContent += `<div class="stock-data">${formatStockData(data.stock_data)}</div>`;
        }
        
        // Add news data if available
        if (data && data.news_data) {
            messageContent += `<div class="news-data">${formatNewsData(data.news_data)}</div>`;
        }
        
        messageElement.innerHTML = messageContent;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    
    // Function to format stock data
    function formatStockData(stockData) {
        if (typeof stockData === 'string') {
            return stockData;
        }
        
        if (typeof stockData === 'object') {
            return `<pre>${JSON.stringify(stockData, null, 2)}</pre>`;
        }
        
        return stockData;
    }
    
    // Function to format news data
    function formatNewsData(newsData) {
        if (typeof newsData === 'string') {
            // Convert plain text news to HTML with proper formatting
            return newsData
                .replace(/📰 (.*?)(?=\n)/g, '<div class="news-title">📰 $1</div>')
                .replace(/📅 (.*?)(?=\n)/g, '<div class="news-date">📅 $1</div>')
                .replace(/📊 (.*?)(?=\n)/g, '<div class="news-sentiment">📊 $1</div>')
                .replace(/📈 (.*?)(?=\n)/g, '<div class="news-relevance">📈 $1</div>')
                .replace(/🔗 (.*?)(?=\n)/g, '<div class="news-source">🔗 $1</div>')
                .replace(/📝 (.*?)(?=\n)/g, '<div class="news-description">📝 $1</div>')
                .replace(/🌐 (.*?)(?=\n|$)/g, '<div class="news-url"><a href="$1" target="_blank">🌐 Read Full Article</a></div>')
                .replace(/\n\n/g, '<div class="news-separator"></div>')
                .replace(/\n/g, '<br>');
        }
        
        if (typeof newsData === 'object') {
            return `<pre>${JSON.stringify(newsData, null, 2)}</pre>`;
        }
        
        return newsData;
    }
    
    // Function to format trading advice with highlighted recommendations
    function formatTradingAdvice(message) {
        if (typeof message === 'string') {
            // Extract recommendation and confidence score
            const recommendationMatch = message.match(/\*\*RECOMMENDATION:\s*([^*]+)\*\*/);
            const scoreMatch = message.match(/\*\*CONFIDENCE SCORE:\s*([^*]+)\*\*/);
            
            let formattedMessage = message;
            
            // Format recommendation with larger font and appropriate color
            if (recommendationMatch) {
                const recommendation = recommendationMatch[1].trim();
                const recommendationClass = getRecommendationClass(recommendation);
                formattedMessage = formattedMessage.replace(
                    /\*\*RECOMMENDATION:\s*([^*]+)\*\*/,
                    `<div class="trading-recommendation ${recommendationClass}">📊 RECOMMENDATION: ${recommendation}</div>`
                );
            }
            
            // Format confidence score with larger font
            if (scoreMatch) {
                const score = scoreMatch[1].trim();
                formattedMessage = formattedMessage.replace(
                    /\*\*CONFIDENCE SCORE:\s*([^*]+)\*\*/,
                    `<div class="trading-confidence">🎯 CONFIDENCE SCORE: ${score}</div>`
                );
            }
            
            // Add separator between recommendation and detailed analysis
            formattedMessage = formattedMessage.replace(
                /(<div class="trading-confidence">.*?<\/div>)/,
                '$1<div class="trading-separator"></div>'
            );
            
            // Convert line breaks to HTML
            formattedMessage = formattedMessage.replace(/\n/g, '<br>');
            
            return formattedMessage;
        }
        
        return message;
    }
    
    // Function to get CSS class for recommendation type
    function getRecommendationClass(recommendation) {
        const rec = recommendation.toUpperCase();
        if (rec.includes('BUY')) return 'rec-buy';
        if (rec.includes('SELL')) return 'rec-sell';
        if (rec.includes('HOLD')) return 'rec-hold';
        return 'rec-neutral';
    }
    
    // Function to add message to input history
    function addToHistory(message) {
        if (message.trim() && message !== inputHistory[0]) {
            inputHistory.unshift(message);
            if (inputHistory.length > MAX_HISTORY) {
                inputHistory.pop();
            }
        }
        historyIndex = -1;
    }
    
    // Function to navigate history
    function navigateHistory(direction) {
        if (inputHistory.length === 0) return;
        
        if (direction === 'up') {
            if (historyIndex < inputHistory.length - 1) {
                historyIndex++;
                messageInput.value = inputHistory[historyIndex];
                messageInput.classList.add('history-mode');
            }
        } else if (direction === 'down') {
            if (historyIndex > 0) {
                historyIndex--;
                messageInput.value = inputHistory[historyIndex];
                messageInput.classList.add('history-mode');
            } else if (historyIndex === 0) {
                historyIndex = -1;
                messageInput.value = '';
                messageInput.classList.remove('history-mode');
            }
        }
        
        // Move cursor to end of input
        messageInput.setSelectionRange(messageInput.value.length, messageInput.value.length);
    }
    
    // Function to send message
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            addToHistory(message);
            addMessage(message, 'user');
            socket.emit('message_from_user', { message: message });
            messageInput.value = '';
            messageInput.classList.remove('history-mode');
        }
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            navigateHistory('up');
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            navigateHistory('down');
        } else if (e.key === 'Escape') {
            // Clear history mode on Escape
            historyIndex = -1;
            messageInput.classList.remove('history-mode');
        }
    });
    
    // Clear history mode when user starts typing
    messageInput.addEventListener('input', (e) => {
        if (historyIndex !== -1) {
            historyIndex = -1;
            messageInput.classList.remove('history-mode');
        }
    });
    
    // Handle personality selection
    personalityList.addEventListener('click', (e) => {
        if (e.target.classList.contains('personality-item')) {
            const personality = e.target.dataset.personality;
            
            // Update active class
            document.querySelectorAll('.personality-item').forEach(item => {
                item.classList.remove('active');
            });
            e.target.classList.add('active');
            
            // Update current personality display
            currentPersonalityName.textContent = personality;
            currentPersonality = personality;
            
            // Send personality change to server
            socket.emit('personality_change', { personality: personality });
            
            // Add message to chat and history
            const personalityMessage = `Change personality to ${personality}`;
            addToHistory(personalityMessage);
            addMessage(personalityMessage, 'user');
        }
    });
    
    // Socket event handlers
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });
    
    socket.on('message_from_server', (data) => {
        const message = data.message || data;
        const personality = data.personality || currentPersonality;
        const stockData = data.data || null;
        
        addMessage(message, 'bot', personality, stockData);
    });
    
    socket.on('personality_updated', (data) => {
        currentPersonality = data.personality;
        currentPersonalityName.textContent = data.personality;
        
        if (data.message) {
            addMessage(data.message, 'bot', data.personality);
        }
    });
    
    socket.on('error', (error) => {
        console.error('Socket error:', error);
        addMessage('Connection error. Please refresh the page.', 'bot');
    });
    
    // Auto-focus on message input
    messageInput.focus();
}); 