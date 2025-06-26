from knest_backend.apps.circles.models import Circle
from knest_backend.apps.interests.models import Interest

def fix_circle_interests():
    """サークルに適切な興味関心を関連付ける"""
    
    print("🔧 サークルに興味関心を関連付け中...")
    
    try:
        # 利用可能な興味関心を取得
        interests = Interest.objects.all()
        print(f"利用可能な興味関心: {interests.count()}件")
        
        if interests.count() == 0:
            print("❌ 興味関心データがありません")
            return
            
        # 興味関心の名前をリスト表示
        print("\n利用可能な興味関心:")
        for i, interest in enumerate(interests, 1):
            print(f"  {i}. {interest.name}")
        
        # サークルに興味関心を関連付け
        circles = Circle.objects.all()
        print(f"\nサークル: {circles.count()}件")
        
        for circle in circles:
            current_interests = circle.interests.all()
            print(f"\n🎯 {circle.name}")
            print(f"  現在の興味関心: {[i.name for i in current_interests]}")
            
            # サークル名に基づいて適切な興味関心を関連付け
            if "読書" in circle.name:
                # 読書関連の興味関心を探す
                book_interests = interests.filter(name__icontains="読書")
                if not book_interests.exists():
                    book_interests = interests.filter(name__icontains="文学")
                if not book_interests.exists():
                    book_interests = interests.filter(name__icontains="学習")
                    
                if book_interests.exists():
                    circle.interests.add(book_interests.first())
                    print(f"  ✅ 追加: {book_interests.first().name}")
                    
            elif "デザイン" in circle.name:
                # デザイン関連の興味関心を探す
                design_interests = interests.filter(name__icontains="デザイン")
                if not design_interests.exists():
                    design_interests = interests.filter(name__icontains="アート")
                if not design_interests.exists():
                    design_interests = interests.filter(name__icontains="クリエイティブ")
                    
                if design_interests.exists():
                    circle.interests.add(design_interests.first())
                    print(f"  ✅ 追加: {design_interests.first().name}")
                    
            elif "カフェ" in circle.name:
                # カフェ・食事関連の興味関心を探す
                cafe_interests = interests.filter(name__icontains="グルメ")
                if not cafe_interests.exists():
                    cafe_interests = interests.filter(name__icontains="食事")
                if not cafe_interests.exists():
                    cafe_interests = interests.filter(name__icontains="料理")
                    
                if cafe_interests.exists():
                    circle.interests.add(cafe_interests.first())
                    print(f"  ✅ 追加: {cafe_interests.first().name}")
                    
            elif "フットサル" in circle.name:
                # スポーツ関連の興味関心を探す
                sports_interests = interests.filter(name__icontains="スポーツ")
                if not sports_interests.exists():
                    sports_interests = interests.filter(name__icontains="サッカー")
                if not sports_interests.exists():
                    sports_interests = interests.filter(name__icontains="運動")
                    
                if sports_interests.exists():
                    circle.interests.add(sports_interests.first())
                    print(f"  ✅ 追加: {sports_interests.first().name}")
                    
            elif "iOS" in circle.name or "開発" in circle.name:
                # テクノロジー・開発関連の興味関心を探す
                tech_interests = interests.filter(name__icontains="プログラミング")
                if not tech_interests.exists():
                    tech_interests = interests.filter(name__icontains="開発")
                if not tech_interests.exists():
                    tech_interests = interests.filter(name__icontains="テクノロジー")
                if not tech_interests.exists():
                    tech_interests = interests.filter(name__icontains="IT")
                    
                if tech_interests.exists():
                    circle.interests.add(tech_interests.first())
                    print(f"  ✅ 追加: {tech_interests.first().name}")
            
            # 汎用的な興味関心も追加（マッチング率向上のため）
            if circle.interests.count() == 0:
                # 何も関連付けられていない場合は最初の興味関心を追加
                first_interest = interests.first()
                if first_interest:
                    circle.interests.add(first_interest)
                    print(f"  📌 汎用追加: {first_interest.name}")
        
        # 結果確認
        print("\n✅ 関連付け完了後の状況:")
        for circle in circles:
            interests_list = [i.name for i in circle.interests.all()]
            print(f"  - {circle.name}: {interests_list}")
            
        print(f"\n🎉 すべてのサークルに興味関心を関連付けました！")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_circle_interests() 