import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi, UserCreateInput } from '../../api/users';
import { User, Role } from '../../types';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Select } from '../../components/ui/Select';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/Table';
import { EmptyState } from '../../components/ui/EmptyState';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { formatDate } from '../../utils/formatters';
import { Plus, Users, Shield, Key } from 'lucide-react';

export const UsersPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  // Form State
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [roleId, setRoleId] = useState<number | undefined>(undefined);
  const [formError, setFormError] = useState<string | null>(null);

  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.list(),
  });

  const { data: roles } = useQuery({
    queryKey: ['roles'],
    queryFn: () => usersApi.listRoles(),
  });

  const createMutation = useMutation({
    mutationFn: (data: UserCreateInput) => usersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setIsModalOpen(false);
      resetForm();
    },
    onError: (err: any) => {
      setFormError(err.response?.data?.detail || 'Failed to create user account');
    },
  });

  const resetForm = () => {
    setFullName('');
    setEmail('');
    setPassword('');
    setRoleId(roles && roles.length > 0 ? roles[0].id : undefined);
    setFormError(null);
  };

  const handleCreateUser = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !email.trim() || !password || !roleId) {
      setFormError('Please fill in all required fields');
      return;
    }
    createMutation.mutate({
      full_name: fullName.trim(),
      email: email.trim(),
      password,
      role_id: Number(roleId),
    });
  };

  const getRoleBadgeVariant = (roleName: string) => {
    switch (roleName?.toLowerCase()) {
      case 'admin':
        return 'danger';
      case 'sales':
        return 'gold';
      case 'finance':
        return 'purple';
      case 'support':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <div className="page-container space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[#1C1410] font-display flex items-center gap-2">
            Users & Role-Based Access Control
          </h1>
          <p className="text-xs text-[#7A6860] mt-1">
            Provision staff credentials, review active roles, and govern granular system permissions.
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => {
            resetForm();
            if (roles && roles.length > 0) setRoleId(roles[0].id);
            setIsModalOpen(true);
          }}
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Provision User Account
        </Button>
      </div>

      {/* Users Table */}
      {isLoading ? (
        <LoadingSpinner />
      ) : !users || users.length === 0 ? (
        <EmptyState
          title="No users found"
          description="Provision internal team members to enable role-based operational workflows."
          actionLabel="Provision User"
          onAction={() => {
            resetForm();
            setIsModalOpen(true);
          }}
        />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User Name</TableHead>
              <TableHead>Email Address</TableHead>
              <TableHead>Assigned Role</TableHead>
              <TableHead>Permissions</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created Date</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((u) => {
              const roleName = u.role?.name || 'Staff';
              const badgeVariant = getRoleBadgeVariant(roleName);

              return (
                <TableRow key={u.id}>
                  <TableCell>
                    <div className="font-semibold text-[#1C1410]">{u.full_name}</div>
                  </TableCell>
                  <TableCell className="font-mono text-xs text-[#7A6860]">
                    {u.email}
                  </TableCell>
                  <TableCell>
                    <Badge variant={badgeVariant as any} dot>
                      {roleName.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1 max-w-xs">
                      {(u.permissions || []).slice(0, 3).map((perm) => (
                        <span
                          key={perm}
                          className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#FAF7F2] border border-[#E2D9D0] text-[#7A6860]"
                        >
                          {perm}
                        </span>
                      ))}
                      {(u.permissions?.length || 0) > 3 && (
                        <span className="text-[10px] text-[#7A6860] self-center">
                          +{u.permissions.length - 3} more
                        </span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={u.is_active ? 'success' : 'default'} dot>
                      {u.is_active ? 'Active' : 'Suspended'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-[#7A6860]">
                    {formatDate(u.created_at)}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setSelectedUser(u)}
                    >
                      Inspect RBAC
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}

      {/* User RBAC Detail Modal */}
      {selectedUser && (
        <Modal
          isOpen={!!selectedUser}
          onClose={() => setSelectedUser(null)}
          title={`RBAC Profile: ${selectedUser.full_name}`}
          description={`Assigned to ${selectedUser.role?.name?.toUpperCase()} role`}
        >
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-[#F2EDE6] border border-[#E2D9D0] space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-[#7A6860]">Email:</span>
                <span className="font-mono text-[#1C1410]">{selectedUser.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#7A6860]">Role:</span>
                <span className="font-semibold text-[#6B1A2A]">{selectedUser.role?.name?.toUpperCase()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#7A6860]">Account Status:</span>
                <span className="text-[#2D6A4F] font-semibold">{selectedUser.is_active ? 'Active' : 'Inactive'}</span>
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-[#1C1410] uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-[#6B1A2A]" />
                Granted Permissions ({selectedUser.permissions?.length || 0})
              </p>
              <div className="p-3 rounded-lg bg-[#FAF7F2] border border-[#E2D9D0] max-h-48 overflow-y-auto space-y-1">
                {(selectedUser.permissions || []).map((perm) => (
                  <div key={perm} className="flex items-center gap-2 text-xs">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#6B1A2A]" />
                    <span className="font-mono text-[#1C1410]">{perm}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t border-[#E2D9D0]">
              <Button variant="secondary" onClick={() => setSelectedUser(null)}>
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Create User Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Provision New Staff User"
        description="Create an internal staff account with designated department role."
      >
        <form onSubmit={handleCreateUser} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-[#FFE5E5] border border-[#8B1A1A]/30 text-xs text-[#8B1A1A]">
              {formError}
            </div>
          )}

          <Input
            label="Full Name"
            placeholder="e.g. Vikram Sharma"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />

          <Input
            label="Email Address"
            type="email"
            placeholder="vikram@brightloop.io"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <Input
            label="Initial Password (min 6 characters)"
            type="password"
            placeholder="Enter secure password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <Select
            label="Role Assignment"
            value={roleId || ''}
            onChange={(e) => setRoleId(Number(e.target.value))}
            options={(roles || []).map((r) => ({
              value: r.id,
              label: `${r.name.toUpperCase()} — ${r.description || 'System Role'}`,
            }))}
            required
          />

          <div className="flex justify-end gap-3 pt-4 border-t border-[#E2D9D0]">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={createMutation.isPending}>
              Provision Account
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
export default UsersPage;

