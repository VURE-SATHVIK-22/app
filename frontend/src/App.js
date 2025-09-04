import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Textarea } from "./components/ui/textarea";
import { Badge } from "./components/ui/badge";
import { Alert, AlertDescription } from "./components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Heart, Shield, MessageCircle, Phone, BookOpen, Users, Send, AlertTriangle, Sparkles } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Generate anonymous session ID
const getSessionId = () => {
  let sessionId = localStorage.getItem('mental_wellness_session');
  if (!sessionId) {
    sessionId = 'anon_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    localStorage.setItem('mental_wellness_session', sessionId);
  }
  return sessionId;
};

const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,rgba(59,130,246,0.05)_1px,transparent_0)] bg-[size:40px_40px]"></div>
      
      <div className="container mx-auto px-6 text-center relative z-10">
        <div className="max-w-4xl mx-auto">
          {/* Hero Badge */}
          <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium mb-8 border border-blue-200">
            <Shield className="w-4 h-4 mr-2" />
            Completely Anonymous & Safe
          </div>
          
          {/* Main Heading */}
          <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 bg-clip-text text-transparent mb-6 leading-tight">
            Your Safe Space for
            <span className="block">Mental Wellness</span>
          </h1>
          
          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-3xl mx-auto leading-relaxed">
            AI-powered, confidential support designed specifically for Indian youth. 
            Break the stigma, find your voice, and access help without judgment.
          </p>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              size="lg" 
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
              onClick={() => document.getElementById('chat-section').scrollIntoView({ behavior: 'smooth' })}
            >
              <MessageCircle className="w-5 h-5 mr-2" />
              Start Anonymous Chat
            </Button>
            <Button 
              variant="outline" 
              size="lg" 
              className="border-2 border-slate-300 hover:border-slate-400 px-8 py-4 text-lg font-semibold rounded-xl hover:bg-slate-50 transition-all duration-300"
              onClick={() => document.getElementById('resources-section').scrollIntoView({ behavior: 'smooth' })}
            >
              <BookOpen className="w-5 h-5 mr-2" />
              Wellness Resources
            </Button>
          </div>
          
          {/* Trust Indicators */}
          <div className="mt-16 grid md:grid-cols-3 gap-8 max-w-3xl mx-auto">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-slate-800 mb-2">100% Anonymous</h3>
              <p className="text-slate-600 text-sm">No personal data stored. Your privacy is protected.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Heart className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-slate-800 mb-2">Culturally Aware</h3>
              <p className="text-slate-600 text-sm">Understands Indian family and social contexts.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Phone className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-slate-800 mb-2">Crisis Support</h3>
              <p className="text-slate-600 text-sm">Immediate access to professional helplines.</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Hero Image */}
      <div className="absolute bottom-0 right-0 w-1/3 h-1/3 opacity-10">
        <img 
          src="https://images.unsplash.com/photo-1506126613408-eca07ce68773?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw0fHxtZW50YWwlMjB3ZWxsbmVzc3xlbnwwfHx8fDE3NTY5OTgzODF8MA&ixlib=rb-4.1.0&q=85" 
          alt="Mental wellness"
          className="w-full h-full object-cover rounded-tl-3xl"
        />
      </div>
    </section>
  );
};

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showCrisisAlert, setShowCrisisAlert] = useState(false);
  const [crisisHelplines, setCrisisHelplines] = useState(null);
  const messagesEndRef = useRef(null);
  const sessionId = getSessionId();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Welcome message
  useEffect(() => {
    setMessages([{
      id: 'welcome',
      type: 'ai',
      content: "नमस्ते! I'm here to listen and support you. This is a safe, anonymous space where you can share your thoughts and feelings without any judgment. How are you feeling today?",
      timestamp: new Date()
    }]);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        session_id: sessionId,
        message: inputMessage
      });

      const aiMessage = {
        id: response.data.id,
        type: 'ai',
        content: response.data.response,
        timestamp: new Date(response.data.timestamp),
        isCrisis: response.data.is_crisis
      };

      setMessages(prev => [...prev, aiMessage]);

      if (response.data.is_crisis) {
        setShowCrisisAlert(true);
        setCrisisHelplines(response.data.helplines);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now().toString(),
        type: 'ai',
        content: "I'm having trouble connecting right now. If you're in crisis, please call a mental health helpline immediately. Your wellbeing is important.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="chat-section" className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-6 max-w-4xl">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-slate-800 mb-4">Anonymous AI Support Chat</h2>
          <p className="text-slate-600 text-lg">Share your thoughts safely with our culturally-aware AI companion</p>
        </div>

        {showCrisisAlert && crisisHelplines && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              <strong>Crisis Support Available:</strong> If you're having thoughts of self-harm, please reach out to professional help:
              <div className="mt-2 space-y-1">
                {Object.values(crisisHelplines).map((helpline, index) => (
                  <div key={index} className="text-sm">
                    <strong>{helpline.name}:</strong> {helpline.number} ({helpline.hours})
                  </div>
                ))}
              </div>
            </AlertDescription>
          </Alert>
        )}

        <Card className="shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-t-lg">
            <CardTitle className="flex items-center text-xl">
              <MessageCircle className="w-6 h-6 mr-2" />
              Your Safe Space Chat
              <Badge variant="secondary" className="ml-auto bg-white/20 text-white">
                Anonymous Session
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {/* Messages Area */}
            <div className="h-96 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-white to-slate-50">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-sm ${
                      message.type === 'user'
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white'
                        : 'bg-white border border-slate-200 text-slate-800'
                    } ${message.isCrisis ? 'border-red-300 bg-red-50' : ''}`}
                  >
                    <p className="text-sm leading-relaxed">{message.content}</p>
                    <p className={`text-xs mt-2 ${message.type === 'user' ? 'text-white/70' : 'text-slate-500'}`}>
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3 max-w-xs">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-6 border-t border-slate-200 bg-white">
              <div className="flex space-x-3">
                <Textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Share your thoughts, feelings, or concerns..."
                  className="flex-1 resize-none border-slate-300 focus:border-blue-500 rounded-xl"
                  rows={2}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                />
                <Button
                  onClick={sendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                  className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-xl px-6 py-3 self-end"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-xs text-slate-500 mt-2">
                💡 This AI provides supportive conversation, not professional medical advice. In crisis? Contact emergency services or call the helplines above.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

const WellnessResources = () => {
  const [resources, setResources] = useState([]);
  const [helplines, setHelplines] = useState({});

  useEffect(() => {
    const fetchResources = async () => {
      try {
        const [resourcesRes, helplinesRes] = await Promise.all([
          axios.get(`${API}/wellness-resources`),
          axios.get(`${API}/helplines`)
        ]);
        setResources(resourcesRes.data.resources);
        setHelplines(helplinesRes.data.helplines);
      } catch (error) {
        console.error('Error fetching resources:', error);
      }
    };
    fetchResources();
  }, []);

  return (
    <section id="resources-section" className="py-20 bg-white">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-slate-800 mb-4">Wellness Resources</h2>
          <p className="text-slate-600 text-lg max-w-2xl mx-auto">
            Practical tools and information to support your mental health journey
          </p>
        </div>

        <Tabs defaultValue="techniques" className="max-w-6xl mx-auto">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="techniques" className="text-base">Coping Techniques</TabsTrigger>
            <TabsTrigger value="helplines" className="text-base">Crisis Support</TabsTrigger>
            <TabsTrigger value="about" className="text-base">About Us</TabsTrigger>
          </TabsList>
          
          <TabsContent value="techniques" className="space-y-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {resources.map((resource) => (
                <Card key={resource.id} className="hover:shadow-lg transition-shadow duration-300 border-0 shadow-md">
                  <CardHeader className="pb-4">
                    <CardTitle className="text-lg text-slate-800 flex items-center">
                      <Sparkles className="w-5 h-5 mr-2 text-blue-500" />
                      {resource.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-slate-600 mb-4 leading-relaxed">{resource.content}</p>
                    <div className="flex flex-wrap gap-2">
                      {resource.tags.map((tag, index) => (
                        <Badge key={index} variant="secondary" className="text-xs bg-blue-100 text-blue-700">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="helplines" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {Object.entries(helplines).map(([key, helpline], index) => (
                <Card key={index} className="border-l-4 border-l-red-400 shadow-md">
                  <CardHeader>
                    <CardTitle className="text-lg text-slate-800 flex items-center">
                      <Phone className="w-5 h-5 mr-2 text-red-500" />
                      {helpline.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <p className="text-2xl font-bold text-red-600">{helpline.number}</p>
                      <p className="text-slate-600"><strong>Hours:</strong> {helpline.hours}</p>
                      <p className="text-slate-600">{helpline.description}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <Alert className="border-amber-200 bg-amber-50">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              <AlertDescription className="text-amber-800">
                <strong>Emergency:</strong> If you're in immediate danger, call 100 (Police) or 108 (Emergency Medical Services) in India.
              </AlertDescription>
            </Alert>
          </TabsContent>
          
          <TabsContent value="about" className="space-y-6">
            <div className="max-w-4xl mx-auto">
              <Card className="shadow-lg border-0">
                <CardContent className="p-8">
                  <div className="grid md:grid-cols-2 gap-8 items-center">
                    <div>
                      <h3 className="text-2xl font-bold text-slate-800 mb-4">Our Mission</h3>
                      <p className="text-slate-600 leading-relaxed mb-4">
                        We're breaking the stigma around mental health in India by providing a safe, anonymous, 
                        and culturally-sensitive platform for youth to seek support and guidance.
                      </p>
                      <p className="text-slate-600 leading-relaxed mb-6">
                        Our AI is designed to understand the unique pressures faced by Indian youth - from 
                        academic stress to family expectations - and provide empathetic, non-judgmental support.
                      </p>
                      <div className="space-y-3">
                        <div className="flex items-center text-slate-700">
                          <Shield className="w-5 h-5 mr-3 text-blue-500" />
                          <span>Complete anonymity and privacy protection</span>
                        </div>
                        <div className="flex items-center text-slate-700">
                          <Heart className="w-5 h-5 mr-3 text-red-500" />
                          <span>Culturally-aware and empathetic responses</span>
                        </div>
                        <div className="flex items-center text-slate-700">
                          <Users className="w-5 h-5 mr-3 text-green-500" />
                          <span>Built specifically for Indian youth</span>
                        </div>
                      </div>
                    </div>
                    <div className="relative">
                      <img 
                        src="https://images.unsplash.com/photo-1541976844346-f18aeac57b06?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwxfHx0aGVyYXB5fGVufDB8fHx8MTc1Njk3MTM4M3ww&ixlib=rb-4.1.0&q=85" 
                        alt="Support and connection"
                        className="w-full h-64 object-cover rounded-xl shadow-lg"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </section>
  );
};

const Footer = () => {
  return (
    <footer className="bg-slate-900 text-white py-12">
      <div className="container mx-auto px-6">
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4 text-blue-400">Mental Wellness AI</h3>
            <p className="text-slate-300 leading-relaxed">
              Supporting Indian youth through anonymous, AI-powered mental health conversations. 
              Your journey to wellness starts here.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4 text-slate-200">Important Notice</h4>
            <p className="text-slate-300 text-sm leading-relaxed">
              This AI provides supportive conversation and is not a replacement for professional 
              therapy or medical treatment. If you're experiencing a mental health crisis, 
              please contact emergency services or professional helplines immediately.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4 text-slate-200">Privacy & Security</h4>
            <ul className="text-slate-300 text-sm space-y-2">
              <li>✓ Fully anonymous sessions</li>
              <li>✓ No personal data stored</li>
              <li>✓ Blockchain-secured conversations</li>
              <li>✓ Culturally-sensitive AI responses</li>
            </ul>
          </div>
        </div>
        <div className="border-t border-slate-700 mt-8 pt-8 text-center">
          <p className="text-slate-400">
            © 2025 Mental Wellness AI. Supporting Indian youth mental health with compassion and privacy.
          </p>
        </div>
      </div>
    </footer>
  );
};

const Home = () => {
  return (
    <div className="min-h-screen">
      <Hero />
      <ChatInterface />
      <WellnessResources />
      <Footer />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;