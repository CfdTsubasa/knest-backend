from knest_backend.apps.users.models import User
from knest_backend.apps.circles.models import Circle
from knest_backend.apps.interests.models import UserInterestProfile, Interest
from knest_backend.apps.recommendations.engines import NextGenRecommendationEngine

def debug_user_recommendations():
    """特定ユーザーの推薦が表示されない原因を調査"""
    
    print("=" * 60)
    print("🔍 ユーザー推薦問題の詳細調査")
    print("=" * 60)
    
    try:
        # 1. ユーザー検索
        print("\n1️⃣ ユーザー検索...")
        users = User.objects.filter(username__icontains="6363")
        print(f"「6363」を含むユーザー: {users.count()}件")
        
        if users.count() == 0:
            print("❌ テストユーザー6363が見つかりません")
            
            # 全ユーザーを表示
            all_users = User.objects.all()[:10]
            print(f"\n📋 既存ユーザー一覧（最初の10件）:")
            for user in all_users:
                print(f"   - {user.username} (ID: {user.id})")
            return
        
        user = users.first()
        print(f"✅ 対象ユーザー: {user.username} (ID: {user.id})")
        
        # 2. 興味関心データ確認
        print("\n2️⃣ 興味関心データ確認...")
        user_interests = UserInterestProfile.objects.filter(user=user)
        print(f"登録済み興味関心: {user_interests.count()}件")
        
        if user_interests.count() == 0:
            print("❌ 興味関心が登録されていません")
            
            # 利用可能な興味関心を表示
            available_interests = Interest.objects.all()[:10]
            print(f"\n📋 利用可能な興味関心（最初の10件）:")
            for interest in available_interests:
                print(f"   - {interest.name}")
        else:
            print("✅ 登録済み興味関心:")
            for interest in user_interests:
                print(f"   - レベル{interest.level}: {interest.category.name if interest.category else 'N/A'}")
                if interest.subcategory:
                    print(f"     └ サブカテゴリ: {interest.subcategory.name}")
                if interest.tag:
                    print(f"     └ タグ: {interest.tag.name}")
        
        # 3. サークルデータ確認
        print("\n3️⃣ サークルデータ確認...")
        total_circles = Circle.objects.count()
        open_circles = Circle.objects.filter(status='open').count()
        user_circles = Circle.objects.filter(
            memberships__user=user,
            memberships__status='active'
        ).count()
        
        print(f"総サークル数: {total_circles}件")
        print(f"募集中サークル: {open_circles}件")
        print(f"ユーザー参加中: {user_circles}件")
        
        if open_circles == 0:
            print("❌ 募集中のサークルがありません")
            return
        
        # 推薦対象外サークルを除外した数
        available_circles = Circle.objects.filter(status='open').exclude(
            memberships__user=user,
            memberships__status='active'
        ).count()
        print(f"推薦対象サークル: {available_circles}件")
        
        # 4. 推薦エンジンのテスト
        print("\n4️⃣ 推薦エンジンテスト...")
        engine = NextGenRecommendationEngine(user)
        
        # ユーザープロファイル分析
        user_profile = engine._analyze_user_profile()
        print(f"ユーザープロファイル: {user_profile}")
        
        # アルゴリズム重み計算
        weights = engine.calculate_algorithm_weights()
        print(f"アルゴリズム重み: {weights}")
        
        # 各エンジンの個別テスト
        print("\n--- 階層マッチングエンジンテスト ---")
        hierarchical_results = engine._get_hierarchical_recommendations(10)
        print(f"階層マッチング結果: {len(hierarchical_results)}件")
        
        if len(hierarchical_results) > 0:
            print("上位3件:")
            for i, (circle, score) in enumerate(hierarchical_results[:3], 1):
                print(f"   {i}. {circle.name}: スコア {score:.3f}")
        else:
            print("❌ 階層マッチングで候補が見つかりません")
            
            # 階層マッチングの詳細調査
            print("\n🔍 階層マッチング詳細調査...")
            hierarchical_matcher = engine.hierarchical_matcher
            user_hierarchical_interests = hierarchical_matcher.user_interests
            print(f"ユーザーの階層興味関心データ: {user_hierarchical_interests}")
            
            # サンプルサークルとのマッチングテスト
            sample_circles = Circle.objects.filter(status='open')[:3]
            for circle in sample_circles:
                match_score = hierarchical_matcher.calculate_circle_match_score(circle)
                print(f"   [{circle.name}] マッチスコア: {match_score:.3f}")
                
                # サークルの興味関心を表示
                circle_interests = circle.interests.all()
                print(f"     サークル興味関心: {[i.name for i in circle_interests]}")
        
        print("\n--- 協調フィルタリングエンジンテスト ---")
        collaborative_results = engine._get_collaborative_recommendations(10)
        print(f"協調フィルタリング結果: {len(collaborative_results)}件")
        
        print("\n--- 行動ベースエンジンテスト ---")
        behavioral_results = engine._get_behavioral_recommendations(10)
        print(f"行動ベース結果: {len(behavioral_results)}件")
        
        # 5. 統合推薦テスト
        print("\n5️⃣ 統合推薦テスト...")
        try:
            recommendations = engine.generate_recommendations(algorithm='smart', limit=5)
            rec_count = len(recommendations['recommendations'])
            print(f"✅ 統合推薦結果: {rec_count}件")
            
            if rec_count == 0:
                print("❌ 統合推薦でも結果が0件です")
                print("\n🔍 原因分析:")
                print("- 興味関心とサークルの関連付けに問題がある可能性")
                print("- マッチングアルゴリズムの閾値が高すぎる可能性")
                print("- データの整合性に問題がある可能性")
                
                # フォールバック推薦をテスト
                print("\n🔄 フォールバック推薦テスト...")
                fallback_circles = Circle.objects.filter(status='open').exclude(
                    memberships__user=user,
                    memberships__status='active'
                )[:3]
                
                print(f"フォールバック候補: {fallback_circles.count()}件")
                for circle in fallback_circles:
                    print(f"   - {circle.name} (メンバー: {circle.member_count}人)")
            else:
                print("✅ 推薦が正常に生成されました")
                for i, rec in enumerate(recommendations['recommendations'], 1):
                    circle = rec['circle']
                    score = rec['score']
                    print(f"   {i}. {circle.name}: スコア {score:.3f}")
                    
        except Exception as e:
            print(f"❌ 統合推薦でエラー: {e}")
            import traceback
            traceback.print_exc()
        
        # 6. 推薦条件の確認
        print("\n6️⃣ 推薦条件確認...")
        
        # ユーザーが既に参加しているサークルを確認
        user_memberships = Circle.objects.filter(
            memberships__user=user,
            memberships__status='active'
        )
        print(f"参加中サークル: {user_memberships.count()}件")
        if user_memberships.count() > 0:
            for circle in user_memberships:
                print(f"   - {circle.name}")
        
        # 推薦対象サークルの詳細
        candidate_circles = Circle.objects.filter(status='open').exclude(
            memberships__user=user,
            memberships__status='active'
        )
        print(f"推薦候補サークル詳細:")
        for circle in candidate_circles:
            interests = circle.interests.all()
            print(f"   - {circle.name}: 興味関心 {[i.name for i in interests]}")
            
    except Exception as e:
        print(f"❌ 調査中にエラーが発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_user_recommendations() 