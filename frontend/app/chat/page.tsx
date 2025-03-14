"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { FiSend, FiMoreVertical, FiSearch, FiCircle, FiSlash, FiFlag, FiArrowLeft, FiLoader } from "react-icons/fi";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { toast, Toaster } from "react-hot-toast";
import { Metadata } from "next";
import WebSocketService from "@/services/websocket";

const metadata: Metadata = {
  title: "Mesajlar | CrushIt",
  description: "CrushIt platformunda mesajlarınızı yönetin."
};

interface ChatUser {
  id: string;
  name: string;
  avatar: string;
  lastMessage: string;
  lastMessageTime: string;
  isOnline: boolean;
  unreadCount?: number;
}

interface Message {
  id: string;
  sender_id: string;
  recipient_id: string;
  content: string;
  timestamp: string;
  is_read: boolean;
}

interface Conversation {
  connection: {
    id: number;
    user1_id: string;
    user2_id: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  };
  user: {
    id: string;
    username: string;
    first_name: string;
    last_name: string;
    is_online: boolean;
    last_online: string;
  };
  recent_message: {
    id: number;
    sender_id: string;
    recipient_id: string;
    content: string;
    is_read: boolean;
    created_at: string;
  } | null;
  unread_count: number;
}

const ChatPage = () => {
  const [activeChat, setActiveChat] = useState<string | null>(null);
  const [activeChatUser, setActiveChatUser] = useState<ChatUser | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState("");
  const [reportDescription, setReportDescription] = useState("");
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { data: session } = useSession();
  const router = useRouter();
  const wsService = useRef<WebSocketService>(WebSocketService.getInstance());

  useEffect(() => {
    document.title = metadata.title as string;

    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    let isActive = true;
  
    if (isActive && session?.user?.accessToken) {
      fetchConversations();
      setupWebSocket();
    }
  
    return () => {
      isActive = false;
      wsService.current.disconnect(); // Clean up on unmount
    };
  }, [session]);

  useEffect(() => {
    if (activeChat) {
      fetchMessages(activeChat);
    }
  }, [activeChat]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

const setupWebSocket = () => {
  if (!session?.user?.accessToken || !process.env.NEXT_PUBLIC_BACKEND_API_URL) {
    console.log('Missing session or API URL, cannot set up WebSocket');
    return;
  }

  // First, clean up by disconnecting any existing connection
  wsService.current.disconnect();

  // Define handlers
  const handleWsMessage = (data: any) => {
    if (data.type === 'message') {
        if (activeChat && (data.sender_id === activeChat || data.recipient_id === activeChat)) {
          // Add the new message to the current chat
          const newMsg: Message = {
            id: Date.now().toString(),
            sender_id: data.sender_id,
            recipient_id: session.user.id,
            content: data.content,
            timestamp: data.timestamp,
            is_read: false
          };
          
          setMessages(prevMessages => [...prevMessages, newMsg]);
        }
        
        // Refresh conversations to update last message and unread count
        fetchConversations();
    }
  };

  const handleWsConnect = () => {
    console.log('WebSocket connected successfully');
    setWsConnected(true);
  };

  const handleWsDisconnect = () => {
    console.log('WebSocket disconnected');
    setWsConnected(false);
  };

  const handleWsError = (error: Event) => {
    console.error('WebSocket error occurred');
    setWsConnected(false);
    // Don't show a toast on initial error - this can be annoying for users
  };

  // Clear any existing handlers
  wsService.current.removeMessageHandler(handleWsMessage);
  wsService.current.removeConnectHandler(handleWsConnect);
  wsService.current.removeDisconnectHandler(handleWsDisconnect);
  wsService.current.removeErrorHandler(handleWsError);

  // Add new handlers
  wsService.current.addMessageHandler(handleWsMessage);
  wsService.current.addConnectHandler(handleWsConnect);
  wsService.current.addDisconnectHandler(handleWsDisconnect);
  wsService.current.addErrorHandler(handleWsError);

  // Initialize connection only once, after a small delay
  setTimeout(() => {
    wsService.current.connect(
      process.env.NEXT_PUBLIC_BACKEND_API_URL,
      session.user.accessToken
    );
  }, 500);
};

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchConversations = async () => {
    if (!session?.user?.accessToken) return;
    
    setIsLoading(true);
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/realtime/conversations`,
        {
          headers: {
            'Authorization': `Bearer ${session.user.accessToken}`,
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch conversations');
      }

      const data: Conversation[] = await response.json();
      setConversations(data);

      // If there's at least one conversation and no active chat,
      // set the first conversation as active
      if (data.length > 0 && !activeChat) {
        setActiveChat(data[0].user.id);
        setActiveChatUser({
          id: data[0].user.id,
          name: `${data[0].user.first_name} ${data[0].user.last_name}`,
          avatar: '/images/defaults/man-default.png', // You might want to fetch the actual avatar
          lastMessage: data[0].recent_message?.content || 'Henüz mesaj yok',
          lastMessageTime: data[0].recent_message ? new Date(data[0].recent_message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '',
          isOnline: data[0].user.is_online,
          unreadCount: data[0].unread_count
        });
      }
    } catch (error) {
      console.error('Conversations fetch error:', error);
      toast.error('Konuşmalar yüklenemedi');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchMessages = async (userId: string) => {
    if (!session?.user?.accessToken) return;
    
    setIsLoadingMessages(true);
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/realtime/messages/${userId}`,
        {
          headers: {
            'Authorization': `Bearer ${session.user.accessToken}`,
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch messages');
      }

      const data: Message[] = await response.json();
      setMessages(data);
      
      // Update the conversations to mark messages as read
      const updatedConversations = conversations.map(conv => {
        if (conv.user.id === userId) {
          return { ...conv, unread_count: 0 };
        }
        return conv;
      });
      
      setConversations(updatedConversations);
    } catch (error) {
      console.error('Messages fetch error:', error);
      toast.error('Mesajlar yüklenemedi');
    } finally {
      setIsLoadingMessages(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !activeChat || !session?.user?.accessToken) return;
    
    // Generate a temporary ID for optimistic updates
    const tempId = `temp-${Date.now()}`;
    
    try {
      // Optimistically add the message to the UI
      const tempMessage: Message = {
        id: tempId,
        sender_id: session.user.id,
        recipient_id: activeChat,
        content: newMessage,
        timestamp: new Date().toISOString(),
        is_read: false
      };
      
      setMessages(prev => [...prev, tempMessage]);
      setNewMessage("");
      
      // Check if WebSocket is connected before sending
      if (!wsService.current.isConnected()) {
        throw new Error('WebSocket is not connected');
      }
      
      // Send via WebSocket
      wsService.current.send({
        type: 'message',
        recipientId: activeChat,
        content: newMessage
      });
      
      // After successful send, fetch conversations to update UI
      setTimeout(() => {
        fetchConversations();
      }, 1000);
      
    } catch (error) {
      console.error('Send message error:', error);
      toast.error('Mesaj gönderilemedi');
      
      // Remove the temporary message on failure
      setMessages(prev => prev.filter(msg => msg.id !== tempId));
      
      // If WebSocket failed, try REST API as fallback
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/realtime/messages`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${session.user.accessToken}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              recipient_id: activeChat,
              content: newMessage
            })
          }
        );
  
        if (response.ok) {
          // If REST API works, add the message back to UI
          const data = await response.json();
          setMessages(prev => [...prev, {
            id: data.id,
            sender_id: session.user.id,
            recipient_id: activeChat,
            content: newMessage,
            timestamp: data.created_at,
            is_read: false
          }]);
          
          toast.success('Mesaj gönderildi (yedek kanal)');
          fetchConversations();
        }
      } catch (fallbackError) {
        console.error('Fallback send failed:', fallbackError);
      }
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSelectChat = (userId: string, user: ChatUser) => {
    setActiveChat(userId);
    setActiveChatUser(user);
  };

  const handleBlock = () => {
    setShowBlockModal(true);
    setShowMenu(false);
  };

  const handleReport = () => {
    setShowReportModal(true);
    setShowMenu(false);
  };

  const confirmBlock = async () => {
    if (!session?.user?.accessToken || !activeChat) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/interactions/block`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.user.accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            blocked_id: activeChat
          })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to block user');
      }

      toast.success('Kullanıcı engellendi');
      setShowBlockModal(false);
      
      // Remove the conversation from the list
      setConversations(prev => prev.filter(conv => conv.user.id !== activeChat));
      setActiveChat(null);
    } catch (error) {
      console.error('Block error:', error);
      toast.error('Kullanıcı engellenemedi');
    }
  };

  const submitReport = async () => {
    if (!session?.user?.accessToken || !activeChat) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/interactions/report`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.user.accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            reported_id: activeChat,
            reason: reportReason,
            description: reportDescription
          })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to report user');
      }

      toast.success('Kullanıcı rapor edildi');
      setShowReportModal(false);
      setReportReason("");
      setReportDescription("");
    } catch (error) {
      console.error('Report error:', error);
      toast.error('Kullanıcı rapor edilemedi');
    }
  };

/*   if (!session) {
    return (
      <section className="pt-[150px] pb-[120px] bg-[#1C1C1E] min-h-screen">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-white mb-4">Erişim Engellendi</h1>
            <p className="text-gray-300 mb-8">Bu sayfayı görüntülemek için giriş yapmalısınız.</p>
            <button 
              onClick={() => router.push('/signin')}
              className="px-6 py-3 bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white rounded-lg"
            >
              Giriş Yap
            </button>
          </div>
        </div>
      </section>
    );
  } */

  return (
    <section className="pt-[80px] md:pt-[150px] pb-[60px] md:pb-[120px] bg-[#1C1C1E] min-h-screen">
      <Toaster position="top-right" />
      <div className="container mx-auto px-4">
        <div className="flex flex-col lg:flex-row bg-[#2C2C2E] rounded-xl overflow-hidden"
          style={{ height: "calc(100vh - 160px)" }}>
          {/* Chat List - Make it full width on mobile */}
          <div className={`${activeChat ? 'hidden lg:block' : 'block'} lg:w-1/3 border-r border-[#3C3C3E]`}>
            <div className="sticky top-0 bg-[#2C2C2E] p-4 border-b border-[#3C3C3E] z-10">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Sohbet ara..."
                  className="w-full bg-[#3C3C3E] text-white rounded-lg pl-10 pr-4 py-3 focus:ring-2 focus:ring-[#D63384] transition-all"
                />
                <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              </div>
            </div>

            {/* Chat List Scrollable Area */}
            <div className="overflow-y-auto h-[calc(100vh-240px)] scrollbar-thin scrollbar-thumb-[#3C3C3E] scrollbar-track-transparent">
              {isLoading ? (
                <div className="flex items-center justify-center h-full">
                  <FiLoader className="w-8 h-8 text-[#D63384] animate-spin" />
                </div>
              ) : conversations.length > 0 ? (
                conversations.map((conv) => (
                  <motion.div
                    key={conv.user.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`p-4 flex items-center cursor-pointer hover:bg-[#3C3C3E] transition-all ${
                      activeChat === conv.user.id ? "bg-[#3C3C3E]" : ""
                    }`}
                    onClick={() => handleSelectChat(conv.user.id, {
                      id: conv.user.id,
                      name: `${conv.user.first_name} ${conv.user.last_name}`,
                      avatar: '/images/defaults/man-default.png',
                      lastMessage: conv.recent_message?.content || 'Henüz mesaj yok',
                      lastMessageTime: conv.recent_message 
                        ? formatTimestamp(conv.recent_message.created_at) 
                        : '',
                      isOnline: conv.user.is_online,
                      unreadCount: conv.unread_count
                    })}
                  >
                    <div className="relative">
                      <div className="w-12 h-12 rounded-full overflow-hidden">
                        <Image
                          src="/images/defaults/man-default.png" // Replace with actual profile picture
                          alt={conv.user.first_name}
                          fill
                          className="object-cover"
                        />
                      </div>
                      {conv.user.is_online && (
                        <div className="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-green-500 border-2 border-[#2C2C2E]" />
                      )}
                    </div>

                    <div className="ml-3 flex-1">
                      <div className="flex justify-between items-start">
                        <h3 className="text-white font-semibold">
                          {conv.user.first_name} {conv.user.last_name}
                        </h3>
                        <span className="text-xs text-gray-400">
                          {conv.recent_message 
                            ? formatTimestamp(conv.recent_message.created_at)
                            : ''}
                        </span>
                      </div>
                      <p className="text-gray-400 text-sm truncate">
                        {conv.recent_message?.content || 'Henüz mesaj yok'}
                      </p>
                    </div>

                    {conv.unread_count > 0 && (
                      <div className="ml-2 bg-[#D63384] rounded-full w-5 h-5 flex items-center justify-center">
                        <span className="text-white text-xs">{conv.unread_count}</span>
                      </div>
                    )}
                  </motion.div>
                ))
              ) : (
                <div className="flex flex-col items-center justify-center h-full p-4 text-center">
                  <p className="text-gray-400 mb-2">Henüz aktif sohbet bulunmuyor</p>
                  <p className="text-gray-500 text-sm">
                    Birileriyle "eşleştiğinizde" burada onlarla sohbet edebilirsiniz
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Block Confirmation Modal */}
          {showBlockModal && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-[#2C2C2E] rounded-xl p-6 max-w-md w-full mx-4">
                <h3 className="text-xl text-white font-semibold mb-4">Kullanıcıyı Engelle</h3>
                <p className="text-gray-300 mb-6">
                  Bu kullanıcıyı engellemek istediğinizden emin misiniz? Engellediğiniz kullanıcılar sizinle iletişim kuramaz.
                </p>
                <div className="flex justify-end space-x-4">
                  <button
                    onClick={() => setShowBlockModal(false)}
                    className="px-4 py-2 text-gray-300 hover:text-white"
                  >
                    İptal
                  </button>
                  <button
                    onClick={confirmBlock}
                    className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                  >
                    Engelle
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Report Modal */}
          {showReportModal && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-[#2C2C2E] rounded-xl p-6 max-w-md w-full mx-4">
                <h3 className="text-xl text-white font-semibold mb-4">Kullanıcıyı Raporla</h3>

                <div className="mb-4">
                  <label className="block text-gray-300 mb-2">Raporlama Nedeni</label>
                  <select
                    value={reportReason}
                    onChange={(e) => setReportReason(e.target.value)}
                    className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2"
                  >
                    <option value="">Seçiniz</option>
                    <option value="spam">Spam</option>
                    <option value="harassment">Taciz</option>
                    <option value="inappropriate">Uygunsuz İçerik</option>
                    <option value="fake">Sahte Profil</option>
                    <option value="other">Diğer</option>
                  </select>
                </div>

                <div className="mb-6">
                  <label className="block text-gray-300 mb-2">Açıklama</label>
                  <textarea
                    value={reportDescription}
                    onChange={(e) => setReportDescription(e.target.value)}
                    className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 min-h-[100px]"
                    placeholder="Lütfen detaylı açıklama yapınız..."
                  />
                </div>

                <div className="flex justify-end space-x-4">
                  <button
                    onClick={() => {
                      setShowReportModal(false);
                      setReportReason("");
                      setReportDescription("");
                    }}
                    className="px-4 py-2 text-gray-300 hover:text-white"
                  >
                    İptal
                  </button>
                  <button
                    onClick={submitReport}
                    disabled={!reportReason || !reportDescription}
                    className="px-4 py-2 bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white rounded-lg hover:opacity-90 disabled:opacity-50"
                  >
                    Raporla
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Chat Area */}
          <div className={`${activeChat ? 'block' : 'hidden lg:block'} flex-1 flex flex-col`}>
            {activeChat ? (
              <>
                {/* Chat Header with Back Button on Mobile */}
                <div className="sticky top-0 bg-[#2C2C2E] p-4 border-b border-[#3C3C3E] flex items-center justify-between z-10">
                  <div className="flex items-center">
                    <button
                      className="lg:hidden mr-3 text-gray-400 hover:text-white"
                      onClick={() => setActiveChat(null)}
                    >
                      <FiArrowLeft size={20} />
                    </button>
                    <div className="relative">
                      <div className="w-10 h-10 rounded-full overflow-hidden">
                        <Image
                          src="/images/defaults/man-default.png" // Replace with actual avatar
                          alt="Active chat"
                          fill
                          className="object-cover"
                        />
                      </div>
                      {activeChatUser?.isOnline && (
                        <div className="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-green-500 border border-[#2C2C2E]" />
                      )}
                    </div>
                    <div className="ml-3">
                      <h3 className="text-white font-semibold">
                        {activeChatUser?.name}
                      </h3>
                      <p className="text-xs text-gray-400">
                        {activeChatUser?.isOnline ? 'Çevrimiçi' : 'Çevrimdışı'}
                      </p>
                    </div>
                  </div>
          
                  <div className="relative" ref={menuRef}>
                    <button
                      className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-[#3C3C3E]"
                      onClick={() => setShowMenu(!showMenu)}
                    >
                      <FiMoreVertical size={20} />
                    </button>
          
                    {showMenu && (
                      <div className="absolute right-0 mt-2 w-48 bg-[#2C2C2E] rounded-lg shadow-lg py-2 z-50">
                        <button
                          onClick={handleBlock}
                          className="w-full px-4 py-2 text-left text-white hover:bg-[#3C3C3E] flex items-center"
                        >
                          <FiSlash className="mr-2" />
                          Engelle
                        </button>
                        <button
                          onClick={handleReport}
                          className="w-full px-4 py-2 text-left text-red-500 hover:bg-[#3C3C3E] flex items-center"
                        >
                          <FiFlag className="mr-2" />
                          Raporla
                        </button>
                      </div>
                    )}
                  </div>
                </div>
          
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-[#3C3C3E] scrollbar-track-transparent">
                  {isLoadingMessages ? (
                    <div className="flex items-center justify-center h-full">
                      <FiLoader className="w-8 h-8 text-[#D63384] animate-spin" />
                    </div>
                  ) : messages.length > 0 ? (
                    messages.map((message) => (
                      <motion.div
                        key={message.id}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.2 }}
                        className={`flex ${message.sender_id === session.user.id ? "justify-end" : "justify-start"}`}
                      >
                        {message.sender_id !== session.user.id && (
                          <div className="w-8 h-8 rounded-full overflow-hidden mr-2 flex-shrink-0">
                            <Image
                              src="/images/defaults/man-default.png" // Replace with actual avatar
                              alt="User avatar"
                              width={32}
                              height={32}
                              className="object-cover"
                            />
                          </div>
                        )}
                        <div
                          className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                            message.sender_id === session.user.id
                              ? "bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white"
                              : "bg-[#3C3C3E] text-white"
                          }`}
                        >
                          <p className="leading-relaxed">{message.content}</p>
                          <span className="text-xs text-gray-300 mt-2 block">
                            {formatTimestamp(message.timestamp)}
                          </span>
                        </div>
                      </motion.div>
                    ))
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full">
                      <p className="text-gray-400">Henüz mesaj yok</p>
                      <p className="text-gray-500 text-sm mt-2">Sohbete başlamak için mesaj gönderin</p>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
          
                {/* Message Input */}
                <form onSubmit={handleSendMessage} className="sticky bottom-0 bg-[#2C2C2E] p-4 border-t border-[#3C3C3E]">
                  <div className="flex items-center space-x-4">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Mesajınızı yazın..."
                      className="flex-1 bg-[#3C3C3E] text-white rounded-lg px-4 py-3 focus:ring-2 focus:ring-[#D63384] transition-all"
                    />
                    <motion.button
                      type="submit"
                      whileTap={{ scale: 0.95 }}
                      disabled={!newMessage.trim()}
                      className="p-3 rounded-full bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white disabled:opacity-50 transition-all hover:shadow-lg"
                    >
                      <FiSend size={20} />
                    </motion.button>
                  </div>
                </form>
              </>
            ) : (
              <div className="h-[calc(100vh-300px)] flex items-center justify-center">
                <div className="text-center">
                  <p className="text-gray-400 text-lg">
                    Sohbet başlatmak için bir kişi seçin
                  </p>
                  <p className="text-gray-500 text-sm mt-2">
                    {conversations.length > 0 
                      ? "Sol taraftan bir sohbet seçebilirsiniz" 
                      : "Henüz hiç eşleşmeniz yok"}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default ChatPage;