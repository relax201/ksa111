<?php

namespace App\Http\Controllers\Notification;

use App\Http\Controllers\Controller;
use App\Models\Notification;
use App\Models\NotificationSetting;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Auth;

class NotificationController extends Controller
{
    /**
     * عرض قائمة الإشعارات للمستخدم مع عدد غير المقروءة.
     */
    public function index(Request $request): JsonResponse
    {
        $userId = Auth::id();
        $perPage = (int) $request->get('per_page', 20);

        $notifications = Notification::where('user_id', $userId)
            ->latest()
            ->paginate($perPage);

        $unreadCount = Notification::where('user_id', $userId)
            ->unread()
            ->count();

        return response()->json([
            'success'      => true,
            'data'         => $notifications->items(),
            'unread_count' => $unreadCount,
            'pagination'   => [
                'total'        => $notifications->total(),
                'per_page'     => $notifications->perPage(),
                'current_page' => $notifications->currentPage(),
                'last_page'    => $notifications->lastPage(),
            ],
        ]);
    }

    /**
     * تحديد إشعار محدد كمقروء.
     */
    public function markAsRead(Request $request, string $id): JsonResponse
    {
        $notification = Notification::where('id', $id)
            ->where('user_id', Auth::id())
            ->first();

        if (!$notification) {
            return response()->json([
                'success' => false,
                'message' => 'الإشعار غير موجود',
            ], 404);
        }

        $notification->update(['is_read' => true]);

        return response()->json([
            'success' => true,
            'message' => 'تم تحديد الإشعار كمقروء',
        ]);
    }

    /**
     * تحديد جميع إشعارات المستخدم كمقروءة.
     */
    public function markAllAsRead(Request $request): JsonResponse
    {
        $count = Notification::where('user_id', Auth::id())
            ->unread()
            ->update(['is_read' => true]);

        return response()->json([
            'success' => true,
            'updated' => $count,
            'message' => 'تم تحديد جميع الإشعارات كمقروءة',
        ]);
    }

    /**
     * جلب إعدادات الإشعارات أو تحديثها.
     */
    public function updateSettings(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'email_notifications'   => 'boolean',
            'price_alerts'          => 'boolean',
            'recommendation_alerts' => 'boolean',
            'market_news'           => 'boolean',
        ]);

        $settings = NotificationSetting::updateOrCreate(
            ['user_id' => Auth::id()],
            $validated
        );

        return response()->json([
            'success'  => true,
            'settings' => $settings,
            'message'  => 'تم تحديث إعدادات الإشعارات بنجاح',
        ]);
    }
}
