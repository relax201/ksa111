<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('portfolios', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('user_id')->index();
            $table->string('name', 100);
            $table->string('description', 500)->nullable();
            $table->string('currency', 3)->default('SAR');
            $table->timestamps();
        });

        Schema::create('portfolio_stocks', function (Blueprint $table) {
            $table->id();
            $table->foreignId('portfolio_id')->constrained()->cascadeOnDelete();
            $table->string('symbol', 20);
            $table->decimal('quantity', 15, 4);
            $table->decimal('purchase_price', 15, 4);
            $table->date('purchase_date')->nullable();
            $table->string('notes', 500)->nullable();
            $table->timestamps();

            $table->index(['portfolio_id', 'symbol']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('portfolio_stocks');
        Schema::dropIfExists('portfolios');
    }
};
