"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Network, Lock, Users, Zap, AlertCircle, MessageCircle, X } from "lucide-react";
import ChatBot from "react-chatbotify";

interface NetworkPolicy {
  id: string;
  department: string;
  resourceAccess: string[];
  bandwidth: number;
  priority: "low" | "medium" | "high";
  enabled: boolean;
}

interface SDNController {
  id: string;
  name: string;
  status: "online" | "offline";
  connectedDevices: number;
  uptime: string;
}

export default function NetworkManagementPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);
  const [showChatbot, setShowChatbot] = useState(false);
  const [policies, setPolicies] = useState<NetworkPolicy[]>([
    {
      id: "1",
      department: "ICU",
      resourceAccess: ["sensors", "alerts", "analytics"],
      bandwidth: 100,
      priority: "high",
      enabled: true,
    },
    {
      id: "2",
      department: "Radiology",
      resourceAccess: ["sensors", "devices"],
      bandwidth: 50,
      priority: "medium",
      enabled: true,
    },
  ]);

  const [controllers, setControllers] = useState<SDNController[]>([
    {
      id: "1",
      name: "Main Controller",
      status: "online",
      connectedDevices: 45,
      uptime: "99.8%",
    },
    {
      id: "2",
      name: "Backup Controller",
      status: "online",
      connectedDevices: 12,
      uptime: "98.5%",
    },
  ]);

  const [newPolicy, setNewPolicy] = useState<{
    department: string;
    resourceAccess: string[];
    bandwidth: number;
    priority: "low" | "medium" | "high";
  }>({
    department: "",
    resourceAccess: ["sensors"],
    bandwidth: 50,
    priority: "medium",
  });

  const [showNewPolicyForm, setShowNewPolicyForm] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const chatbotFlow = {
    start: {
      message: "👋 Welcome to Network Intent Assistant! I can help you express your network access requirements in natural language. What would you like to do?",
      path: "menu",
    },
    menu: {
      message: "What would you like assistance with?",
      options: ["Create Network Policy", "View Policies", "Manage Bandwidth", "Security Help"],
      path: (params: { userInput: string }) => {
        const input = params.userInput.toLowerCase();
        if (input.includes("policy") || input.includes("create")) {
          return "create_policy";
        } else if (input.includes("view") || input.includes("policies")) {
          return "view_policies";
        } else if (input.includes("bandwidth") || input.includes("limit")) {
          return "bandwidth";
        } else if (input.includes("security") || input.includes("help")) {
          return "security";
        }
        return "menu";
      },
    },
    create_policy: {
      message: "📋 To create a network policy, tell me: Which department needs access? (e.g., 'ICU needs access to sensors and alerts with 100 Mbps')",
      options: ["Back to Menu"],
      path: (params: { userInput: string }) => {
        if (params.userInput.toLowerCase().includes("back")) return "menu";
        return "create_policy";
      },
    },
    view_policies: {
      message: "📊 Current network policies are displayed in the Network Policies section above. Each policy shows:\n• Department name\n• Resource access levels\n• Bandwidth allocation\n• Priority level\n• Enable/Disable status",
      options: ["Back to Menu"],
      path: (params: { userInput: string }) => {
        if (params.userInput.toLowerCase().includes("back")) return "menu";
        return "view_policies";
      },
    },
    bandwidth: {
      message: "⚡ Bandwidth management helps allocate network resources. High-priority departments (ICU, Emergency) typically get 100+ Mbps, while standard departments get 50 Mbps. How much bandwidth do you need?",
      options: ["Back to Menu"],
      path: (params: { userInput: string }) => {
        if (params.userInput.toLowerCase().includes("back")) return "menu";
        return "bandwidth";
      },
    },
    security: {
      message: "🔒 Security best practices:\n• Always enable policies for sensitive departments\n• Use HIGH priority for critical services\n• Isolate department access to required resources only\n• Regularly review and update bandwidth limits\n\nNeed anything else?",
      options: ["Back to Menu"],
      path: (params: { userInput: string }) => {
        if (params.userInput.toLowerCase().includes("back")) return "menu";
        return "security";
      },
    },
  };

  // Check if user is admin
  const isAdmin = session?.user?.role === "ADMIN";

  if (!session) {
    router.push("/login");
    return null;
  }

  if (!isAdmin) {
    return (
      <div className="p-6">
        <Alert className="border-destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Access denied. Network management is restricted to administrators only.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const handleAddPolicy = () => {
    if (newPolicy.department.trim()) {
      const policy: NetworkPolicy = {
        id: Date.now().toString(),
        ...newPolicy,
        enabled: true,
      };
      setPolicies([...policies, policy]);
      setNewPolicy({
        department: "",
        resourceAccess: ["sensors"],
        bandwidth: 50,
        priority: "medium",
      });
      setShowNewPolicyForm(false);
    }
  };

  const handleTogglePolicy = (id: string) => {
    setPolicies(
      policies.map((policy) =>
        policy.id === id ? { ...policy, enabled: !policy.enabled } : policy
      )
    );
  };

  const handleDeletePolicy = (id: string) => {
    setPolicies(policies.filter((policy) => policy.id !== id));
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Network className="h-8 w-8 text-primary" />
          Software-Defined Network (SDN) Management
        </h1>
        <p className="text-muted-foreground mt-2">
          Configure network policies, control resource allocation, and manage department access
        </p>
      </div>

      {/* SDN Controllers Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {controllers.map((controller) => (
          <Card key={controller.id}>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                {controller.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Status:</span>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    controller.status === "online"
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {controller.status.toUpperCase()}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Connected Devices:</span>
                <span className="font-semibold">{controller.connectedDevices}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Uptime:</span>
                <span className="font-semibold">{controller.uptime}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Network Policies */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-primary" />
              <div>
                <CardTitle>Network Policies</CardTitle>
                <CardDescription>
                  Manage department access and resource allocation
                </CardDescription>
              </div>
            </div>
            <Button onClick={() => setShowNewPolicyForm(true)}>
              + New Policy
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* New Policy Form */}
          {showNewPolicyForm && (
            <div className="border rounded-lg p-4 bg-muted/50 space-y-4">
              <h3 className="font-semibold flex items-center gap-2">
                <Users className="h-4 w-4" />
                Create New Network Policy
              </h3>

              <div className="space-y-3">
                <div>
                  <Label htmlFor="department">Department</Label>
                  <Input
                    id="department"
                    placeholder="e.g., Emergency Department"
                    value={newPolicy.department}
                    onChange={(e) =>
                      setNewPolicy({ ...newPolicy, department: e.target.value })
                    }
                  />
                </div>

                <div>
                  <Label>Bandwidth Limit (Mbps)</Label>
                  <Input
                    type="number"
                    min="10"
                    max="1000"
                    value={newPolicy.bandwidth}
                    onChange={(e) =>
                      setNewPolicy({ ...newPolicy, bandwidth: parseInt(e.target.value) })
                    }
                  />
                </div>

                <div>
                  <Label>Priority Level</Label>
                  <Select
                    value={newPolicy.priority}
                    onValueChange={(value: "low" | "medium" | "high") =>
                      setNewPolicy({ ...newPolicy, priority: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleAddPolicy} className="flex-1">
                    Create Policy
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowNewPolicyForm(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Policies List */}
          <div className="space-y-2">
            {policies.map((policy) => (
              <div
                key={policy.id}
                className="border rounded-lg p-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="font-semibold">{policy.department}</h4>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        policy.priority === "high"
                          ? "bg-red-100 text-red-800"
                          : policy.priority === "medium"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-blue-100 text-blue-800"
                      }`}
                    >
                      {policy.priority.toUpperCase()}
                    </span>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        policy.enabled
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {policy.enabled ? "ENABLED" : "DISABLED"}
                    </span>
                  </div>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p>
                      <strong>Resources:</strong>{" "}
                      {policy.resourceAccess.join(", ")}
                    </p>
                    <p>
                      <strong>Bandwidth:</strong> {policy.bandwidth} Mbps
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant={policy.enabled ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleTogglePolicy(policy.id)}
                  >
                    {policy.enabled ? "Disable" : "Enable"}
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDeletePolicy(policy.id)}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Security Information */}
      <Alert>
        <Lock className="h-4 w-4" />
        <AlertDescription>
          <strong>LLM-Powered Intent Expression:</strong> Non-IT staff can express network
          access intents in natural language, which are automatically converted to secure
          network policies. Each department gets isolated access to only their required
          resources, enforced by the SDN controller.
        </AlertDescription>
      </Alert>

      {/* Floating Network Assistant Chatbot */}
      {isClient && (
        <div className="bg-card rounded-lg border shadow-sm p-6">
          <ChatBot
            flow={chatbotFlow}
            settings={{
              general: {
                embedded: false,
              },
              chatHistory: {
                storageKey: "hospital_chat_history",
              },
            }}
          />
        </div>
      )}
    </div>
  );
}
